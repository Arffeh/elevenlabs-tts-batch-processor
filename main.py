import sys
import os
import re
import struct
import requests
import argparse
from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings
import time
from httpx import ReadTimeout

def load_environment_variables():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    dotenv_path = os.path.join(application_path, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        print(f"No .env file found at {dotenv_path}")

load_environment_variables()

# Initialize ElevenLabs client
api_key = os.getenv('ELEVENLABS_API_KEY')
voice_id = os.getenv('ELEVENLABS_VOICE_ID')
api_url = os.getenv('ELEVENLABS_API_URL', 'https://api.elevenlabs.io/v1')

if not api_key:
    raise ValueError("API key not found. Please set ELEVENLABS_API_KEY in your environment.")
if not voice_id:
    raise ValueError("Voice ID not found. Please set ELEVENLABS_VOICE_ID in your environment.")

# Load voice settings from environment variables
stability = float(os.getenv('ELEVENLABS_STABILITY', 0.5))
similarity_boost = float(os.getenv('ELEVENLABS_SIMILARITY_BOOST', 0.75))
style = float(os.getenv('ELEVENLABS_STYLE', 0.0))
use_speaker_boost = os.getenv('ELEVENLABS_USE_SPEAKER_BOOST', 'True').lower() in ('true', '1', 'yes')
speed = float(os.getenv('ELEVENLABS_SPEED', 1.0))
model_id = os.getenv('ELEVENLABS_MODEL_ID', 'eleven_multilingual_v2')
output_format = os.getenv('ELEVENLABS_OUTPUT_FORMAT', 'ulaw_8000')

# Validate the output format
valid_formats = [
    'mp3_44100',
    'pcm_16000',
    'pcm_22050',
    'pcm_24000',
    'pcm_44100',
    'ulaw_8000'
]
if output_format not in valid_formats:
    raise ValueError(f"Invalid output format: {output_format}. Must be one of {valid_formats}")

client = ElevenLabs(api_key=api_key, base_url=api_url)

def get_next_output_number(directory):
    pattern = re.compile(r'output_(\d{4})\.(mp3|wav)')
    max_number = 0
    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            number = int(match.group(1))
            if number > max_number:
                max_number = number
    return max_number + 1


def add_wav_header(audio_data, audio_format='ulaw', sample_rate=8000, num_channels=1, bits_per_sample=8):
    chunk_id = b'RIFF'
    format = b'WAVE'
    subchunk1_id = b'fmt '
    subchunk2_id = b'data'

    # Set format-specific values
    if audio_format == 'ulaw':
        audio_format_code = 7  # μ-law
        bits_per_sample = 8
    elif audio_format == 'pcm':
        audio_format_code = 1  # PCM
    else:
        raise ValueError("Unsupported audio format. Use 'ulaw' or 'pcm'.")

    subchunk1_size = 16 if audio_format_code == 1 else 18  # 18 for ulaw, 16 for PCM
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    subchunk2_size = len(audio_data)

    chunk_size = 4 + (8 + subchunk1_size) + (8 + subchunk2_size)

    if audio_format_code == 1:  # PCM
        wav_header = struct.pack('<4sI4s4sIHHIIHH4sI',
                                 chunk_id,
                                 chunk_size,
                                 format,
                                 subchunk1_id,
                                 subchunk1_size,
                                 audio_format_code,
                                 num_channels,
                                 sample_rate,
                                 byte_rate,
                                 block_align,
                                 bits_per_sample,
                                 subchunk2_id,
                                 subchunk2_size)
    else:  # μ-law
        wav_header = struct.pack('<4sI4s4sIHHIIHHH4sI',
                                 chunk_id,
                                 chunk_size,
                                 format,
                                 subchunk1_id,
                                 subchunk1_size,
                                 audio_format_code,
                                 num_channels,
                                 sample_rate,
                                 byte_rate,
                                 block_align,
                                 bits_per_sample,
                                 0,  # ExtraParamSize for μ-law
                                 subchunk2_id,
                                 subchunk2_size)

    return wav_header + audio_data


def text_to_speech_file(text, voice_id, output_filename, retries=3, retry_delay=5):
    for attempt in range(retries):
        try:
            # Convert text to speech
            audio_stream = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                output_format=output_format,
                model_id=model_id,
                voice_settings=VoiceSettings(
                    stability=stability,
                    similarity_boost=similarity_boost,
                    style=style,
                    use_speaker_boost=use_speaker_boost,
                    speed=speed
                ),
            )
            audio_data = b''.join(chunk for chunk in audio_stream if chunk)

            if output_format == "ulaw_8000":
                audio_data = add_wav_header(audio_data)
            elif output_format.startswith("pcm"):
                pcm_sample_rate = int(output_format.split("_")[1])
                audio_data = add_wav_header(audio_data, audio_format='pcm', sample_rate=pcm_sample_rate)

            with open(output_filename, "wb") as f:
                f.write(audio_data)

            print(f"A new audio file was saved successfully at {output_filename}")
            break  # Break the loop if successful

        except (ReadTimeout, requests.exceptions.RequestException) as e:
            print(f"Attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
def list_voices():
    response = client.voices.get_all()
    for voice in response.voices:
        print(f"Name: {voice.name}, Voice ID: {voice.voice_id}")

def main():
    parser = argparse.ArgumentParser(description="ElevenLabs TTS Batch Processor")
    parser.add_argument('--list-voices', action='store_true')
    args = parser.parse_args()

    if args.list_voices:
        list_voices()
        return

    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    next_number = get_next_output_number(output_dir)

    with open('input.txt', 'r') as file:
        lines = [line.strip() for line in file if line.strip()]

    extension = 'mp3' if output_format == 'mp3_44100' else 'wav'

    for line in lines:
        output_filename = os.path.join(output_dir, f'output_{next_number:04}.{extension}')
        text_to_speech_file(line, voice_id, output_filename)
        next_number += 1

if __name__ == "__main__":
    main()
