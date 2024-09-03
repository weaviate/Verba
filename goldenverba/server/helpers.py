from fastapi import WebSocket
from goldenverba.server.types import (
    FileStatus,
    StatusReport,
    DataBatchPayload,
    FileConfig,
    CreateNewDocument,
)
from wasabi import msg


class LoggerManager:
    def __init__(self, socket: WebSocket = None):
        self.socket = socket

    async def send_report(
        self, file_Id: str, status: FileStatus, message: str, took: float
    ):
        msg.info(f"{status} | {file_Id} | {message} | {took}")
        if self.socket is not None:
            payload: StatusReport = {
                "fileID": file_Id,
                "status": status,
                "message": message,
                "took": took,
            }

            await self.socket.send_json(payload)

    async def create_new_document(
        self, new_file_id: str, document_name: str, original_file_id: str
    ):
        msg.info(f"Creating new file {new_file_id} from {original_file_id}")
        if self.socket is not None:
            payload: CreateNewDocument = {
                "new_file_id": new_file_id,
                "filename": document_name,
                "original_file_id": original_file_id,
            }

            await self.socket.send_json(payload)


class BatchManager:
    def __init__(self):
        self.batches = {}

    def add_batch(self, payload: DataBatchPayload) -> FileConfig:
        try:
            # msg.info(f"Receiving Batch for {payload.fileID} : {payload.order} of {payload.total}")

            if payload.fileID not in self.batches:
                self.batches[payload.fileID] = {
                    "fileID": payload.fileID,
                    "total": payload.total,
                    "chunks": {},
                }

            self.batches[payload.fileID]["chunks"][payload.order] = payload.chunk

            fileConfig = self.check_batch(payload.fileID)

            if fileConfig is not None or payload.isLastChunk:
                msg.info(f"Removing {payload.fileID} from BatchManager")
                del self.batches[payload.fileID]

            return fileConfig

        except Exception as e:
            msg.fail(f"Failed to add batch to BatchManager: {str(e)}")

    def check_batch(self, fileID: str):
        if len(self.batches[fileID]["chunks"].keys()) == self.batches[fileID]["total"]:
            msg.good(f"Collected all Batches of {fileID}")
            chunks = self.batches[fileID]["chunks"]
            data = "".join([chunks[chunk] for chunk in chunks])
            return FileConfig.model_validate_json(data)
        else:
            return None
