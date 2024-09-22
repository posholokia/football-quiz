from httpx import (
    ASGITransport,
    AsyncClient,
)
from main import create_app


app = create_app()


async def send_post(url, json=None, headers=None):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost:8000"
    ) as session:
        return await session.post(url, json=json, headers=headers)


async def send_get(url, headers=None):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost:8000"
    ) as session:
        return await session.get(url, headers=headers)


async def send_patch(url, json=None, headers=None):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost:8000"
    ) as session:
        return await session.patch(url, json=json, headers=headers)


async def send_put(url, json=None, headers=None):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost:8000"
    ) as session:
        return await session.put(url, json=json, headers=headers)


async def send_delete(url, headers=None):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost:8000"
    ) as session:
        return await session.delete(url, headers=headers)
