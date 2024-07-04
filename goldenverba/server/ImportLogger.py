from fastapi import WebSocket

class LoggerManager:
    def __init__(self, socket: WebSocket):
        self.socket = socket

    async def send_success(self, msg: str = ""):
        print("SUCCES!")
        await self.socket.send_json({"type": "SUCCESS", "message": msg})
    
    async def send_info(self, msg: str = ""):
        print("INFO!")
        await self.socket.send_json({"type": "INFO", "message": msg})
    
    async def send_warning(self, msg: str = ""):
        print("WARNING!")
        await self.socket.send_json({"type": "WARNING", "message": msg})

    async def send_error(self, msg: str = ""):
        print("ERROR!")
        await self.socket.send_json({"type": "ERROR", "message": msg})

    async def send_stop(self):
        print("STOP!")
        await self.socket.send_json({"type": "STOP", "message": ""})