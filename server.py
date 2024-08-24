import httpx
from fastapi import BackgroundTasks, FastAPI, Request
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process(request: Request):
    try:
        await asyncio.sleep(5)
        await send(request.callback_url, {"id": request.id, "result": "OK"})
    except Exception as e:
        logging.error(f"Error processing for request ID {request.id} : {e}")
        raise


app = FastAPI()


@app.post("/vi/inferences")
async def inference(request: Request, background_tasks: BackgroundTasks) -> dict[str, str]:
    background_tasks.add_task(process, request)
    return {"message": "Received"}


async def send(url: str, data: dict[str, str]):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        response.raise_for_status()
        return response
