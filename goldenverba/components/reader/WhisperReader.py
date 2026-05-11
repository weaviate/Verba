import asyncio
import base64
import os
import tempfile

from wasabi import msg

from goldenverba.components.document import Document, create_document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig
from goldenverba.components.types import InputConfig

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None


class WhisperReader(Reader):
    """
    Local Whisper reader for importing audio and video files using faster-whisper.
    Runs entirely locally — no API key or external service required.
    """

    def __init__(self):
        super().__init__()
        self.requires_library = ["faster_whisper"]
        self.extension = [
            ".3ga",
            ".8svx",
            ".aac",
            ".ac3",
            ".aif",
            ".aiff",
            ".alac",
            ".amr",
            ".ape",
            ".au",
            ".dss",
            ".flac",
            ".flv",
            ".m2ts",
            ".m4a",
            ".m4b",
            ".m4p",
            ".m4r",
            ".m4v",
            ".mov",
            ".mp2",
            ".mp3",
            ".mp4",
            ".mpga",
            ".mts",
            ".mxf",
            ".ogg",
            ".oga",
            ".mogg",
            ".opus",
            ".qcp",
            ".ts",
            ".tta",
            ".voc",
            ".wav",
            ".webm",
            ".wma",
            ".wv",
        ]
        self.name = "Whisper"
        self.description = "Transcribes audio and video files locally using faster-whisper. No API key required."
        self.config = {
            "Model Size": InputConfig(
                type="dropdown",
                value="base",
                description="Whisper model size — larger models are more accurate but slower and use more memory",
                values=["tiny", "base", "small", "medium", "large-v3"],
            ),
            "Device": InputConfig(
                type="dropdown",
                value="cpu",
                description="Compute device for inference",
                values=["cpu", "cuda", "auto"],
            ),
        }

    async def load(
        self, config: dict[str, InputConfig], fileConfig: FileConfig
    ) -> list[Document]:
        """
        Transcribe an audio/video file using faster-whisper running locally.
        """
        if WhisperModel is None:
            raise ImportError(
                "faster-whisper is required for audio transcription. "
                "Install it with: pip install faster-whisper"
            )

        model_size = config["Model Size"].value
        device = config["Device"].value

        msg.info(f"Transcribing {fileConfig.filename} with Whisper ({model_size})")

        file_bytes = base64.b64decode(fileConfig.content)

        # faster-whisper needs a file path, not a file-like object
        suffix = f".{fileConfig.extension}" if fileConfig.extension else ".wav"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        try:
            segments, _info = await asyncio.to_thread(
                self._transcribe, model_size, device, tmp_path
            )
            text = " ".join(segment.text.strip() for segment in segments)
            if not text:
                raise Exception(f"Whisper returned empty transcript for {fileConfig.filename}")
            return [create_document(text, fileConfig)]
        finally:
            os.unlink(tmp_path)

    def _transcribe(self, model_size: str, device: str, path: str):
        """Synchronous transcription — called via asyncio.to_thread."""
        model = WhisperModel(model_size, device=device, compute_type="int8")
        segments, info = model.transcribe(path, beam_size=5)
        # Consume the generator inside the thread so it doesn't escape to async context
        return list(segments), info
