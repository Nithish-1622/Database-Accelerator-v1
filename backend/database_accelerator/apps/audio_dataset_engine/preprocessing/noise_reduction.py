from __future__ import annotations

import math
import os
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import numpy as np

try:
    import librosa  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    librosa = None


@dataclass
class AudioPayload:
    waveform: np.ndarray
    sample_rate: int
    source_path: str
    source_format: str


def _to_mono(waveform: np.ndarray) -> np.ndarray:
    if waveform.ndim == 1:
        return waveform.astype(np.float32, copy=False)
    return waveform.mean(axis=1).astype(np.float32, copy=False)


def _resample_numpy(waveform: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
    if source_rate == target_rate or waveform.size == 0:
        return waveform.astype(np.float32, copy=False)
    duration = waveform.shape[0] / float(source_rate)
    target_length = max(1, int(round(duration * target_rate)))
    source_positions = np.linspace(0.0, 1.0, num=waveform.shape[0], endpoint=False)
    target_positions = np.linspace(0.0, 1.0, num=target_length, endpoint=False)
    return np.interp(target_positions, source_positions, waveform).astype(np.float32, copy=False)


def _read_wav(file_path: str) -> AudioPayload:
    with wave.open(file_path, 'rb') as audio_file:
        sample_rate = audio_file.getframerate()
        channels = audio_file.getnchannels()
        sample_width = audio_file.getsampwidth()
        frame_count = audio_file.getnframes()
        raw_frames = audio_file.readframes(frame_count)

    if sample_width == 1:
        waveform = np.frombuffer(raw_frames, dtype=np.uint8).astype(np.float32)
        waveform = (waveform - 128.0) / 128.0
    elif sample_width == 2:
        waveform = np.frombuffer(raw_frames, dtype=np.int16).astype(np.float32) / 32768.0
    elif sample_width == 4:
        waveform = np.frombuffer(raw_frames, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f'Unsupported WAV sample width: {sample_width}')

    if channels > 1:
        waveform = waveform.reshape(-1, channels)
        waveform = _to_mono(waveform)

    return AudioPayload(waveform=waveform, sample_rate=sample_rate, source_path=file_path, source_format='wav')


def load_audio(file_path: str, target_sample_rate: int = 16000) -> AudioPayload:
    suffix = Path(file_path).suffix.lower()
    if librosa is not None:
        waveform, sample_rate = librosa.load(file_path, sr=target_sample_rate, mono=True)
        return AudioPayload(
            waveform=np.asarray(waveform, dtype=np.float32),
            sample_rate=int(sample_rate),
            source_path=file_path,
            source_format=suffix.lstrip('.'),
        )

    if suffix != '.wav':
        raise ValueError('Non-WAV audio loading requires librosa or another decoder dependency.')

    payload = _read_wav(file_path)
    if payload.sample_rate != target_sample_rate:
        payload = AudioPayload(
            waveform=_resample_numpy(payload.waveform, payload.sample_rate, target_sample_rate),
            sample_rate=target_sample_rate,
            source_path=payload.source_path,
            source_format=payload.source_format,
        )
    return payload


def remove_noise(waveform: np.ndarray, sample_rate: int, window_ms: int = 20) -> np.ndarray:
    if waveform.size == 0:
        return waveform.astype(np.float32, copy=False)
    window_size = max(3, int(sample_rate * window_ms / 1000.0))
    kernel = np.ones(window_size, dtype=np.float32) / float(window_size)
    smoothed = np.convolve(waveform.astype(np.float32, copy=False), kernel, mode='same')
    cleaned = waveform.astype(np.float32, copy=False) - (0.35 * smoothed)
    return np.clip(cleaned, -1.0, 1.0)


def trim_silence(waveform: np.ndarray, sample_rate: int, threshold: float = 0.012, min_silence_ms: int = 250) -> np.ndarray:
    if waveform.size == 0:
        return waveform.astype(np.float32, copy=False)

    amplitude = np.abs(waveform.astype(np.float32, copy=False))
    active_mask = amplitude > threshold
    if not np.any(active_mask):
        return waveform[:0].astype(np.float32, copy=False)

    first_active = int(np.argmax(active_mask))
    last_active = int(len(active_mask) - np.argmax(active_mask[::-1]) - 1)

    padding = max(1, int(sample_rate * min_silence_ms / 1000.0))
    start_index = max(0, first_active - padding)
    end_index = min(len(waveform), last_active + padding + 1)
    return waveform[start_index:end_index].astype(np.float32, copy=False)


def normalize_volume(waveform: np.ndarray, target_peak: float = 0.95) -> np.ndarray:
    if waveform.size == 0:
        return waveform.astype(np.float32, copy=False)
    peak = float(np.max(np.abs(waveform)))
    if peak == 0.0:
        return waveform.astype(np.float32, copy=False)
    gain = min(10.0, target_peak / peak)
    normalized = waveform.astype(np.float32, copy=False) * gain
    return np.clip(normalized, -1.0, 1.0)


def segment_audio(waveform: np.ndarray, sample_rate: int, segment_seconds: float = 10.0, overlap_seconds: float = 0.0) -> List[np.ndarray]:
    if waveform.size == 0:
        return []

    segment_length = max(1, int(sample_rate * segment_seconds))
    overlap_length = max(0, int(sample_rate * overlap_seconds))
    step = max(1, segment_length - overlap_length)

    segments: List[np.ndarray] = []
    for start in range(0, len(waveform), step):
        end = start + segment_length
        chunk = waveform[start:end]
        if chunk.size == 0:
            break
        segments.append(chunk.astype(np.float32, copy=False))
        if end >= len(waveform):
            break
    return segments


def write_wav(file_path: str, waveform: np.ndarray, sample_rate: int) -> str:
    output_path = Path(file_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clipped = np.clip(waveform.astype(np.float32, copy=False), -1.0, 1.0)
    pcm = (clipped * 32767.0).astype(np.int16)
    with wave.open(str(output_path), 'wb') as output_file:
        output_file.setnchannels(1)
        output_file.setsampwidth(2)
        output_file.setframerate(sample_rate)
        output_file.writeframes(pcm.tobytes())
    return str(output_path)


def process_audio(file_path: str, output_dir: Optional[str] = None, target_sample_rate: int = 16000) -> dict:
    payload = load_audio(file_path, target_sample_rate=target_sample_rate)
    denoised = remove_noise(payload.waveform, payload.sample_rate)
    trimmed = trim_silence(denoised, payload.sample_rate)
    normalized = normalize_volume(trimmed)
    segments = segment_audio(normalized, payload.sample_rate, segment_seconds=12.0, overlap_seconds=1.0)

    base_dir = Path(output_dir) if output_dir else Path(file_path).parent / 'processed'
    cleaned_path = write_wav(str(base_dir / f'{Path(file_path).stem}_cleaned.wav'), normalized, payload.sample_rate)

    segment_paths = []
    for index, segment in enumerate(segments, start=1):
        segment_path = base_dir / f'{Path(file_path).stem}_segment_{index:03d}.wav'
        segment_paths.append(write_wav(str(segment_path), segment, payload.sample_rate))

    duration_seconds = round(float(len(normalized) / payload.sample_rate), 3) if payload.sample_rate else 0.0
    return {
        'source_path': file_path,
        'source_format': payload.source_format,
        'sample_rate': payload.sample_rate,
        'duration_seconds': duration_seconds,
        'waveform_samples': int(len(normalized)),
        'cleaned_audio_path': cleaned_path,
        'segment_paths': segment_paths,
        'segments_count': len(segment_paths),
    }
