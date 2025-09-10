from collections import deque
from enum import Enum
from typing import List, Optional
from elevenlabs import ElevenLabs
import pyaudio
from io import BytesIO
import numpy as np
import logging

from utils.env_utils import get_environment_variable, is_development

logger = logging.getLogger(__name__)

WAKE_WORDS = ["winston"]

SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE * 0.25)


class ListeningState(Enum):
    WAITING_FOR_WAKE_WORD = 1
    RECORDING_COMMAND = 2
    FINISHED = 3


def audio_stream_generator(stream: pyaudio.Stream, chunk_size: int = CHUNK_SIZE):
    """
    Generator that yields audio chunks from a PyAudio stream.
    """
    while True:
        audio_data = stream.read(chunk_size, exception_on_overflow=False)

        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        audio_array = audio_array.astype(np.float32) / 32768.0

        yield audio_array


def waiting_for_wake_word_handler(
    wake_word_buffer,
    chunk,
    chunk_count,
    state,
    command_buffer,
):
    """
    Handle waiting for wake word if check.
    """
    wake_word_buffer.append(chunk)

    are_chunks_ready = len(wake_word_buffer) >= 4 and chunk_count % 4 == 0
    if not are_chunks_ready:
        return state, command_buffer

    wake_word_list = list(wake_word_buffer)
    audio_to_check = np.concatenate(wake_word_list)
    transcription = transcribe_audio_buffer(audio_to_check)

    is_transcription_ready = transcription and check_wake_word(
        transcription, WAKE_WORDS
    )

    if not is_transcription_ready:
        return state, command_buffer

    if is_development():
        print("🎯 Wake word detected! Recording command...")
    logger.info("🎯 Wake word detected! Switching to command recording mode")

    return ListeningState.RECORDING_COMMAND, list(wake_word_buffer)


def check_audio_stream_for_wake_word(
    audio_source: pyaudio.Stream,
    timeout_seconds: Optional[float] = None,
    silence_threshold: float = 0.01,
    max_silence_seconds: float = 2.0,
) -> Optional[str]:
    """
    Check audio stream for wake word and capture the following command.

    Args:
        audio_source: PyAudio stream
        timeout_seconds: Maximum time to listen (None for no timeout)
        silence_threshold: Threshold for detecting silence
        max_silence_seconds: Seconds of silence before stopping command recording

    Returns:
        Tuple of (wake_word_detected, command_text)
    """
    logger.debug("Starting wake word detection...")
    audio_generator = audio_stream_generator(audio_source)

    wake_word_buffer = deque(maxlen=12)
    command_buffer = []
    state = ListeningState.WAITING_FOR_WAKE_WORD

    consecutive_silence = 0
    max_silence_chunks = int(max_silence_seconds / 0.25)

    chunk_count = 0

    for chunk in audio_generator:
        is_silent = np.abs(chunk).mean() < silence_threshold

        if state == ListeningState.WAITING_FOR_WAKE_WORD:
            new_state, new_command_buffer = waiting_for_wake_word_handler(
                wake_word_buffer, chunk, chunk_count, state, command_buffer
            )

            state = new_state
            command_buffer = new_command_buffer

        if state == ListeningState.RECORDING_COMMAND:
            command_buffer.append(chunk)
            logger.debug(f"Recording command chunk {len(command_buffer)}")

            if not is_silent:
                consecutive_silence = 0
                continue

            consecutive_silence += 1

            if consecutive_silence >= max_silence_chunks:
                state = ListeningState.FINISHED
                logger.info("Silence detected, finishing command recording")
                break

        chunk_count += 1

    audio_source.stop_stream()

    if command_buffer and state == ListeningState.FINISHED:
        full_audio = np.concatenate(command_buffer)
        full_command = eleven_labs_stt(full_audio)
        return full_command

    logger.debug("No command captured")
    return None


def load_whisper_model():
    """
    Load the Whisper model for speech-to-text transcription.
    """
    from whisper import load_model

    return load_model("tiny")


def transcribe_audio_buffer(audio_buffer, model = None):
    """
    Transcribe audio data from a buffer using the Whisper model.
    """
    logger.debug("🎤 Starting Whisper transcription...")
    if model is None:
        model = load_whisper_model()

    result = model.transcribe(audio_buffer, temperature=0.2, without_timestamps=True)
    logger.debug("Whisper transcription completed")

    if result["text"] is None:
        logger.warning("Whisper returned no text")
        return None

    return str(result["text"]).strip()


def check_wake_word(transcribed_audio: str, wake_words: List[str]) -> bool:
    """
    Check if any of the specified wake words are present in the transcribed audio.
    """
    for wake_word in wake_words:
        if wake_word.lower() in transcribed_audio.lower():
            logger.info(f"Wake word '{wake_word}' detected")
            return True

    return False


def eleven_labs_stt(audio_buffer):
    logger.info("Starting ElevenLabs STT transcription...")
    import numpy as np
    import wave

    elevenlabs = ElevenLabs(api_key=get_environment_variable("ELEVENLABS_API_KEY"))
    logger.debug("Initialized ElevenLabs client for STT")

    audio_buffer = np.clip(audio_buffer, -1.0, 1.0)
    audio_int16 = (audio_buffer * 32767).astype(np.int16)
    logger.debug("Audio buffer processed for WAV conversion")

    wav_buffer = BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes for int16
        wav_file.setframerate(16000)
        wav_file.writeframes(audio_int16.tobytes())
    logger.debug("WAV buffer created")

    wav_buffer.seek(0)

    response = elevenlabs.speech_to_text.convert(
        file=wav_buffer,
        model_id="scribe_v1",
        tag_audio_events=True,
    )
    logger.debug("ElevenLabs STT API call completed")

    transcribed_text = response.text
    logger.info(f"ElevenLabs transcription: '{transcribed_text}'")
    return transcribed_text
