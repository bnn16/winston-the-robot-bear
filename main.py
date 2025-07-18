from core.brain import call_llm_with_command
from core.voice.stt import check_audio_stream_for_wake_word
from core.voice.tts import speak_response
from utils.env_utils import (
    load_environment_variables,
)
import pyaudio


def run_interactive_assistant():
    """Run the voice assistant in interactive mode."""
    audio = pyaudio.PyAudio()

    try:
        while True:
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=4000,
            )

            command = check_audio_stream_for_wake_word(
                stream,
                silence_threshold=0.01,
                max_silence_seconds=2.0,
            )

            stream.close()

            if command is None:
                continue

            response = call_llm_with_command(command)
            speak_response(response)
    except KeyboardInterrupt:
        print("\nStopping interactive voice assistant...")
    finally:
        audio.terminate()


def main():
    env = load_environment_variables()

    if env is None:
        return

    run_interactive_assistant()


if __name__ == "__main__":
    main()
