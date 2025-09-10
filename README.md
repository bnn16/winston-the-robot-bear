# Winston the Shitty Robot Stuffed Animal

A voice assistant project built for the "Shitty Robot Challenge" university competition. This quirky AI companion listens for the wake word "Winston" and responds to voice commands with personality and wit.

**Source code by Bogdan Nikolov (@bnn16)**

## Features

- **Wake Word Detection**: Responds to "Winston" using real-time audio processing
- **Speech-to-Text**: Converts voice commands to text using ElevenLabs API
- **AI Processing**: Generates intelligent responses using Google Gemini LLM
- **Text-to-Speech**: Speaks responses back using ElevenLabs TTS
- **Real-time Audio**: Continuous listening with silence detection

## How It Works

1. **Listening Mode**: The assistant continuously monitors audio input for the wake word "Winston"
2. **Command Capture**: Once the wake word is detected, it starts recording the user's command
3. **Silence Detection**: Recording stops after detecting 3 seconds of silence
4. **Transcription**: The recorded audio is sent to ElevenLabs for speech-to-text conversion
5. **AI Processing**: The transcribed text is processed by Google Gemini to generate a response
6. **Voice Response**: The AI response is converted to speech and played back through speakers

## Installation

### Prerequisites
- Python 3.13+
- Microphone access
- API keys for ElevenLabs and Google Gemini

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/bnn16/winston-the-robot-bear
   cd winston-the-robot-bear
   ```

2. **Create virtual environment**
   ```bash
   python -m venv winston-the-robot-bear-env
   ```

3. **Activate the environment**
   ```bash
   source winston-the-robot-bear/bin/activate  # On macOS/Linux
   # or
   winston-the-robot-bear\Scripts\activate     # On Windows
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   
   Create a `.env` file in the root directory with your API keys:
   ```
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## Usage

1. **Start the assistant**
   ```bash
   python main.py
   ```

2. **Interact with the assistant**
   - Say "Hey Winston" to wake it up
   - Follow with your command/question
   - The assistant will process and respond verbally

3. **Stop the assistant**
   - Press `Ctrl+C` to stop the program

## Project Structure

```
assistant-kit/
├── main.py                 # Main entry point
├── core/
│   ├── brain/
│   │   └── llm.py         # LLM integration (Google Gemini)
│   └── voice/
│       ├── stt.py         # Speech-to-text (ElevenLabs)
│       └── tts.py         # Text-to-speech (ElevenLabs)
├── utils/
│   └── env_utils.py       # Environment variable management
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Key Technologies

- **PyAudio**: Real-time audio streaming
- **ElevenLabs**: Speech-to-text and text-to-speech
- **Google Gemini**: Large language model for response generation
- **NumPy**: Audio data processing
- **Whisper**: Local wake word detection (fallback)

## Configuration

You can adjust the following parameters in `main.py`:
- `silence_threshold`: Sensitivity for silence detection (default: 0.01)
- `max_silence_seconds`: Maximum silence before stopping recording (default: 3.0)

## Troubleshooting

- **Audio issues**: Ensure microphone permissions are granted
- **API errors**: Verify your API keys in the `.env` file
- **Getting cut off**: Increase `max_silence_seconds` if commands are being truncated

## License

This project is created for educational purposes as part of a university challenge.

## Author

**Bogdan Nikolov**  
GitHub: [@bnn16](https://github.com/bnn16)