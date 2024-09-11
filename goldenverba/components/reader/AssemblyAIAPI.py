import base64
import io
import os

import requests
from wasabi import msg
import aiohttp
import assemblyai as aai

from goldenverba.components.document import Document, create_document
from goldenverba.components.interfaces import Reader
from goldenverba.server.types import FileConfig
from goldenverba.components.util import get_environment
from goldenverba.components.types import InputConfig


class AssemblyAIReader(Reader):
    """
    AssemblyAI API Reader for importing multiple file types using the AssemblyAI.com API.
    """

    def __init__(self):
        super().__init__()
        self.extension = [
            ".3ga",
            ".webm",
            ".8svx",
            ".mts",
            ".m2ts",
            ".ts",
            ".aac",
            ".mov",
            ".ac3",
            ".mp2",
            ".aif",
            ".mp4",
            ".m4p",
            ".m4v",
            ".aiff",
            ".mxf",
            ".alac",
            ".amr",
            ".ape",
            ".au",
            ".dss",
            ".flac",
            ".flv",
            ".m4a",
            ".m4b",
            ".m4p",
            ".m4r",
            ".mp3",
            ".mpga",
            ".ogg",
            ".oga",
            ".mogg",
            ".opus",
            ".qcp",
            ".tta",
            ".voc",
            ".wav",
            ".wma",
            ".wv",
        ]
        self.requires_env = ["ASSEMBLYAI_API_KEY"]
        self.name = "AssemblyAI"
        self.description = "Uses the AssemblyAI API to import multiple file types such as plain text and documents"
        self.config = {
            "Quality": InputConfig(
                type="dropdown",
                value="best",
                description="Set the transcription quality",
                values=["nano", "best"],
            )
        }

        if os.getenv("ASSEMBLYAI_API_KEY") is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="Set your AssemblyAI API Key here or set it as an environment variable `ASSEMBLYAI_API_KEY`",
                values=[],
            )

    async def load(
        self, config: dict[str, InputConfig], fileConfig: FileConfig
    ) -> list[Document]:
        """
        Load and process a file using the AssemblyAI API.
        """
        # Validate and get API credentials
        token = get_environment(
            config,
            "API Key",
            "ASSEMBLYAI_API_KEY",
            "No AssemblyAI API Key detected",
        )
        aai.settings.api_key = token

        # Validate quality
        quality = config["Quality"].value
        if quality not in ["nano", "best"]:
            raise ValueError(f"Invalid quality: {quality}")

        aaiConfig = aai.TranscriptionConfig(speech_model=aai.SpeechModel.nano)
        if quality == "best":
            aaiConfig = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)

        msg.info(f"Loading {fileConfig.filename}")

        file_data = aiohttp.FormData()
        file_bytes = io.BytesIO(base64.b64decode(fileConfig.content))
        file_data.add_field(
            "files",
            file_bytes,
            filename=f"{fileConfig.filename}.{fileConfig.extension}",
        )

        try:
            transcriber = aai.Transcriber(config=aaiConfig)
            transcript = transcriber.transcribe(file_bytes)
            if transcript.error:
                raise Exception(
                    f"AssemblyAI API failed to transcribe {fileConfig.filename}: {transcript.error}"
                )
            if transcript.text is None:
                raise Exception(
                    f"AssemblyAI API failed to transcribe {fileConfig.filename}, no text returned"
                )
            return [create_document(transcript.text, fileConfig)]

        except requests.RequestException as e:
            raise Exception(
                f"AssemblyAI API request failed for {fileConfig.filename}: {str(e)}"
            )
        except Exception as e:
            raise Exception(f"Failed to process {fileConfig.filename}: {str(e)}")
