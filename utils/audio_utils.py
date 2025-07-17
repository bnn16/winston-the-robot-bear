from typing import Tuple
import numpy as np
import librosa


def load_audio_file(
    file_path: str, target_sr: int = 16000
) -> Tuple[np.ndarray, int | float]:
    """
    Load any audio file using librosa.

    Args:
        file_path: Path to audio file (WAV, MP3, etc.)
        target_sr: Target sample rate (default 16000 for Whisper)

    Returns:
        Tuple of (audio_data, sample_rate)
    """
    audio_data, sample_rate = librosa.load(
        file_path,
        sr=target_sr,
        mono=True,
    )

    return audio_data.astype(np.float32), sample_rate
