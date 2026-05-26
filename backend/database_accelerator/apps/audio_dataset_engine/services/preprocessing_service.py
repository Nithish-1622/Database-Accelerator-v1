from ..preprocessing.noise_reduction import process_audio


class AudioPreprocessingService:
    @staticmethod
    def process(file_path: str, output_dir: str | None = None, target_sample_rate: int = 16000) -> dict:
        return process_audio(file_path=file_path, output_dir=output_dir, target_sample_rate=target_sample_rate)
