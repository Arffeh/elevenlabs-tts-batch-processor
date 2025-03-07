
# Text-to-Speech Batch Processor

This Python script leverages the ElevenLabs API to convert text input into speech, generating audio files in the μ-law WAV format. It reads lines from an `input.txt` file and produces corresponding audio files in the `output/` directory.

## Features

- Batch processing of text lines into speech
- Customizable voice settings
- Dynamic loading of environment variables
- Automatic management of output filenames
- Option to list available voices from the ElevenLabs API

## Prerequisites

- Python 3.x
- An ElevenLabs API key

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Arffeh/elevenlabs-tts-batch-processor.git
   cd tts-batch-processor
   ```


2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```


3. **Configure environment variables:**

   Rename `.env.example` to `.env` and populate it with your specific settings:

   ```bash
   mv .env.example .env
   ```


   Edit the `.env` file to include your ElevenLabs API key and desired voice settings:

   ```
   ELEVENLABS_API_KEY=your_api_key_here
   ELEVENLABS_VOICE_ID=your_voice_id_here
   ELEVENLABS_STABILITY=0.5
   ELEVENLABS_SIMILARITY_BOOST=0.75
   ELEVENLABS_STYLE=0.0
   ELEVENLABS_USE_SPEAKER_BOOST=True
   ELEVENLABS_SPEED=1.0
   ELEVENLABS_MODEL_ID=eleven_multilingual_v2
   ELEVENLABS_OUTPUT_FORMAT=mp3_44100
   ```
   
   The ELEVENLABS_OUTPUT_FORMAT variable accepts strictly the following:
   - mp3_44100
   - pcm_16000
   - pcm_22050
   - pcm_24000
   - pcm_44100
   - ulaw_8000

## Usage

1. **Prepare your input:**

   Create an `input.txt` file in the project directory, with each line representing the text you want to convert to speech.

2. **Run the script:**

   ```bash
   python main.py
   ```


   The script will process each line in `input.txt` and save the resulting audio files in the `output/` directory.

3. **List available voices (optional):**

   To retrieve and display available voice IDs from the ElevenLabs API, use the `--list-voices` flag:

   ```bash
   python main.py --list-voices
   ```


## Packaging as an Executable

To distribute the script as a standalone executable:

1. **Install PyInstaller:**

   ```bash
   pip install -r requirements_pyinstaller.txt
   ```


2. **Create the executable:**

   ```bash
   pyinstaller --onefile main.py
   ```


   This will generate a `dist/main` executable.

3. **Prepare for distribution:**

   Ensure that users have the following files in the same directory as the executable:

   - `input.txt`: The text input file
   - `.env`: The environment configuration file

   Provide users with the `.env.example` file as a template for their own `.env` configuration.

## Notes for Developers

- **Environment Variables:** The script dynamically loads environment variables from a `.env` file located in the same directory as the executable or script. This allows users to provide their own API keys and settings without modifying the code.

- **Output Management:** The script automatically creates an `output/` directory if it doesn't exist and sequentially names output files to prevent overwriting.

- **Voice Settings:** Voice parameters such as stability, similarity boost, style, speaker boost, speed, and model ID are configurable through the `.env` file, offering flexibility without code changes.

- **Error Handling:** Ensure that appropriate error handling is implemented, especially for API interactions and file operations, to enhance robustness.

## License

This project is licensed under the WTFPL License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [ElevenLabs](https://elevenlabs.io/) for their text-to-speech API
- [Python-dotenv](https://github.com/theskumar/python-dotenv) for managing environment variables
- [PyInstaller](https://www.pyinstaller.org/) for packaging the script as an executable
