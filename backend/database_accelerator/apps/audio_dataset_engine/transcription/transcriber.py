from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Optional

try:
    import whisper  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    whisper = None


class WhisperTranscriber:
    def __init__(self, model_name: str = 'small', fallback_model_name: str = 'base'):
        self.model_name = model_name
        self.fallback_model_name = fallback_model_name

    def _load_model(self):
        if whisper is None:
            return None

        try:
            return whisper.load_model(self.model_name)
        except Exception:
            try:
                return whisper.load_model(self.fallback_model_name)
            except Exception:
                return None

    def _fallback_transcript(self, audio_path: str) -> dict:
        stem = Path(audio_path).stem
        words = [part for part in re.split(r'[_\-\s]+', stem) if part]
        if not words:
            words = ['audio', 'upload']
        text = ' '.join(words).strip()
        return {
            'text': f'{text} transcription fallback',
            'language': 'und',
            'provider': 'fallback',
        }

    def audio_to_text(self, audio_path: str, transcript_override: Optional[str] = None) -> dict:
        if transcript_override is not None:
            return {'text': transcript_override, 'language': ''}

        model = self._load_model()
        if model is None:
            return self._fallback_transcript(audio_path)

        try:
            result = model.transcribe(audio_path)
        except FileNotFoundError as e:
            # Usually raised when ffmpeg is not available on PATH (whisper uses ffmpeg subprocess)
            raise RuntimeError(
                "ffmpeg not found: Whisper requires the `ffmpeg` executable on your PATH. "
                "On Windows install ffmpeg (e.g. via Chocolatey: `choco install ffmpeg -y`, "
                "or download from https://ffmpeg.org/download.html) and restart the server.") from e
        except Exception as e:
            # bubble up other exceptions as runtime errors with context
            raise RuntimeError(f'Whisper transcription failed: {e}') from e

        return {
            'text': (result.get('text') or '').strip(),
            'language': result.get('language', '') or '',
            'provider': 'whisper',
        }

    def batch_transcribe(self, audio_paths: Iterable[str], transcript_override: Optional[str] = None) -> List[dict]:
        return [self.audio_to_text(path, transcript_override=transcript_override) for path in audio_paths]

    def segment_transcribe(self, segment_paths: Iterable[str], transcript_override: Optional[str] = None) -> List[dict]:
        transcripts = []
        for segment_path in segment_paths:
            transcripts.append({
                'segment_path': str(segment_path),
                **self.audio_to_text(str(segment_path), transcript_override=transcript_override),
            })
        return transcripts
