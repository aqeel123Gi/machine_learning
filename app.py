from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel
import importlib
import logging
from typing import List

app = FastAPI()

# إعداد قائمة للمتصلين عبر WebSocket
clients = []

# إعداد logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("operation_logs.log"),
        logging.StreamHandler()
    ]
)

# إعداد WebSocketHandler لإرسال السجلات للعملاء
class WebSocketHandler(logging.Handler):
    async def emit(self, record):
        log_entry = self.format(record)
        for client in clients:
            await client.send_text(log_entry)

ws_handler = WebSocketHandler()
ws_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(ws_handler)

# نموذج الإدخال للعملية
class OperationInput(BaseModel):
    operation_name: str
    args: List[int]

# API لتنفيذ العمليات
@app.post("/execute/")
async def execute_operation(operation_input: OperationInput):
    try:
        # استيراد العملية المطلوبة ديناميكيًا
        operation_module = importlib.import_module(f"operations.{operation_input.operation_name}")
        
        # استدعاء دالة `execute` وتنفيذها
        result = operation_module.execute(*operation_input.args)
        logging.info(f"Executed {operation_input.operation_name} with result: {result}")
        return {"status": "success", "result": result}
    
    except ModuleNotFoundError:
        raise HTTPException(status_code=404, detail="Operation not found")
    except Exception as e:
        logging.error(f"Failed to execute {operation_input.operation_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket للسجلات في الوقت الفعلي
@app.websocket("/ws/logs/")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        clients.remove(websocket)