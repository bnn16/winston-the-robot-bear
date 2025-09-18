from core.brain import call_llm_with_command
from core.voice.stt import record_command_on_keypress
from core.voice.tts import speak_response
from core.ui.popup import (
    initialize_window, show_thinking, show_response, 
    show_speaking, show_waiting, show_command_detected
)
from utils.env_utils import (
    load_environment_variables,
)
import pyaudio
import logging
import time
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('assistant.log')
    ]
)
logger = logging.getLogger(__name__)


def run_interactive_assistant():
    """Run the voice assistant in interactive mode."""
    audio = pyaudio.PyAudio()
    
    show_waiting()

    try:
        while True:
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=4000,
            )

            start_time = time.time()
            
            command = record_command_on_keypress(
                stream,
                silence_threshold=0.01,
                max_silence_seconds=3.0,
            )

            stream.close()

            if command is None:
                continue

            logger.info(f"Command received: '{command}'")
            
            show_command_detected(command)
            
            processing_start = time.time()
            logger.info("🤖 Processing command with LLM...")
            
            show_thinking()
            
            response = call_llm_with_command(command)
            processing_time = time.time() - processing_start
            logger.info(f"Command processing time: {processing_time:.2f} seconds")
            
            show_response(response)
            
            logger.info("Generating and playing response...")
            speak_start = time.time()
            
            show_speaking()
            speak_response(response)
            speak_time = time.time() - speak_start
            logger.info(f"Response speaking time: {speak_time:.2f} seconds")
            
            show_waiting()
            
            total_time = time.time() - start_time
            logger.info(f"Total cycle time: {total_time:.2f} seconds")
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, stopping assistant...")
    except Exception as e:
        logger.error(f"Unexpected error in assistant: {e}", exc_info=True)
    finally:
        logger.info("Terminating PyAudio...")
        audio.terminate()
        logger.info("Assistant shutdown complete")


def main():
    logger.info("Starting Winston the Robot Bear...")
    logger.info("Loading environment variables...")
    
    env = load_environment_variables()

    if env is None:
        logger.error("Failed to load environment variables. Please check your .env file.")
        return

    logger.info("Environment variables loaded successfully")
    logger.info("Initializing GUI window...")
    
    window = initialize_window()
    
    assistant_thread = threading.Thread(target=run_interactive_assistant, daemon=True)
    assistant_thread.start()
    
    logger.info("Starting main window loop...")
    
    window.run()


if __name__ == "__main__":
    try:
        logger.info("Starting the assistant...")
        main()
    except Exception as e:
        logger.error(f"Unexpected error in the main execution: {e}", exc_info=True)
