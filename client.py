import asyncio
from fastapi import Request
import uvicorn
import logging
import httpx

url = "http://host.docker.internal:8000/v1/inferences"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_request(data: dict[str, str]):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        logger.info(f"Response from server: {response.json()}")


client_app = FastAPI()


@client_app.post("/v1/results")
async def callback(result: dict[str, str]):
    logger.info(f"Result received: {result}")


def start_server(host: str, port: int):
    config = uvicorn.Config(client_app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, server.run)


if __name__ == "__main__":
    host = "host.docker.internal"
    port = 8001

    start_server(host, port)
    data = {"id": "1234", "callback_url": f"http://{host}:{port}/v1/results"}
    asyncio.run(send_request(data))
