from pydantic import BaseModel, Field
from typing import Optional, Union
from enum import Enum
import asyncio
import websockets
from aiohttp import web
import json

class TaskStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in-progress"

class TaskRequest(BaseModel):
    task_ID: str
    task: str
    requesting_agent_ID: str
    callback_URL: Optional[str] = None

class TaskResponse(BaseModel):
    task_ID: str
    result: str
    status: TaskStatus
    replying_agent_ID: str

class HandoffNotification(BaseModel):
    task_ID: str
    current_agent_ID: str
    new_agent_ID: str
    reason_for_handoff: str

class ClarificationRequest(BaseModel):
    task_ID: str
    question: str
    requesting_agent_id: str

class ClarificationResponse(BaseModel):
    task_ID: str
    answer: str
    replying_agent_id: str

class CallbackNotification(BaseModel):
    task_ID: str
    result: str
    status: TaskStatus
    requesting_agent_ID: str
    replying_agent_ID: str

class ErrorMessage(BaseModel):
    task_ID: Optional[str] = None
    error_message: str
    requesting_agent_ID: str

class TransportInterface:
    async def sendResponse(self, response: Union[TaskResponse, ClarificationResponse, CallbackNotification, ErrorMessage]):
        raise NotImplementedError()

class WebSocketTransport(TransportInterface):
    def __init__(self, websocket):
        self.websocket = websocket

    async def sendResponse(self, response: Union[TaskResponse, ClarificationResponse, CallbackNotification, ErrorMessage]):
        await self.websocket.send(response.json())

class HTTPTransport(TransportInterface):
    def __init__(self, response):
        self.response = response

    async def sendResponse(self, response: Union[TaskResponse, ClarificationResponse, CallbackNotification, ErrorMessage]):
        self.response.text = response.json()
        self.response.content_type = 'application/json'

class AgentServer:
    def __init__(self, port: int = 4242):
        self.port = port
        self.app = web.Application()
        self.app.router.add_post('/task', self.http_task_handler)

    async def start(self):
        self.server = await asyncio.start_server(self.websocket_handler, '0.0.0.0', self.port)
        runner = web.AppRunner(self.app)
        await runner.setup()
        self.site = web.TCPSite(runner, '0.0.0.0', self.port)
        await self.site.start()
        print(f"Server started on port {self.port}")

    async def websocket_handler(self, websocket, path):
        transport = WebSocketTransport(websocket)
        async for message in websocket:
            await self.handleIncomingMessage(json.loads(message), transport)

    async def http_task_handler(self, request):
        data = await request.json()
        response = web.Response()
        transport = HTTPTransport(response)
        await self.handleIncomingMessage(data, transport)
        return response

    async def handleIncomingMessage(self, message: dict, transport: TransportInterface):
        try:
            if 'task' in message:
                await self.handleTaskRequest(TaskRequest(**message), transport)
            elif 'reason_for_handoff' in message:
                await self.handleHandoffNotification(HandoffNotification(**message), transport)
            elif 'question' in message:
                await self.handleClarificationResponse(ClarificationResponse(**message), transport)
            elif 'status' in message:
                await self.handleCallbackNotification(CallbackNotification(**message), transport)
            else:
                raise ValueError("Unknown message type")
        except Exception as e:
            error = ErrorMessage(error_message=str(e), requesting_agent_ID="unknown")
            await self.sendResponse(error, transport)

    async def sendResponse(self, response: Union[TaskResponse, ClarificationResponse, CallbackNotification, ErrorMessage], transport: TransportInterface):
        await transport.sendResponse(response)

    async def handleTaskRequest(self, task_request: TaskRequest, transport: TransportInterface):
        # This method should be overridden in a subclass to implement task processing
        pass

    async def handleHandoffNotification(self, handoff: HandoffNotification, transport: TransportInterface):
        # This method should be overridden in a subclass to implement handoff processing
        pass

    async def handleCallbackNotification(self, callback: CallbackNotification, transport: TransportInterface):
        # This method should be overridden in a subclass to implement callback processing
        pass

    async def handleClarificationResponse(self, clarification: ClarificationResponse, transport: TransportInterface):
        # This method should be overridden in a subclass to implement clarification processing
        pass

if __name__ == "__main__":
    server = AgentServer()
    asyncio.run(server.start())
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("Server stopped")