from fastapi import WebSocket
from goldenverba.server.types import FileStatus
from wasabi import msg

class LoggerManager:
    def __init__(self, socket: WebSocket):
        self.socket = socket

    async def send_report(self, file_Id: str, status: FileStatus, message: str, took: float):
        msg.info(f"{status} | {file_Id} | {message} | {took}")
        payload = {
                    "file_ID": file_Id,
                    "status": status,
                    "report": { status: { "message" : message, "took": took } }
                    }

        await self.socket.send_json(payload)