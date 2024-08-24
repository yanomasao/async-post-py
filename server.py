import asyncio
import logging

import backoff
import httpx
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Request(BaseModel):
    id: str
    callback_url: str


@backoff.on_exception(backoff.expo, (httpx.RequestError, httpx.HTTPStatusError), max_tries=5)
async def send_with_retry(url: str, data: dict[str, str]):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        response.raise_for_status()
    return response


@app.post("/v1/inferences")
async def inference(request: Request, background_tasks: BackgroundTasks) -> dict[str, str]:
    background_tasks.add_task(process, request)
    return {"message": "Received"}


async def process(request: Request):
    try:
        await asyncio.sleep(5)
        await send_with_retry(request.callback_url, {"id": request.id, "result": "OK"})
    except Exception as e:
        logger.error(f"Error processing for request ID {request.id}: {e}")
        raise