from fastapi.requests import Request
import httpx
from fastapi import HTTPException, status, BackgroundTasks
import os


from backgrounds import store_user_data, store_developer_data


async def validate_developer(request: Request, background_tasks: BackgroundTasks):
    async with httpx.AsyncClient() as client:
        client.base_url = os.getenv("AUTH_BASE_URL")
        developer_token = request.headers.get("X-Developer-Token")
        response = await client.get(
            "developer/validate-token", headers={"x-api-token": developer_token}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        data = response.json()
        key = f"dev_{developer_token}"
        background_tasks.add_task(
            store_developer_data, key, data.get("developer").get("id")
        )
        return {"developer_id": data.get("developer").get("id")}


async def validate_app(request: Request, background_tasks: BackgroundTasks):
    async with httpx.AsyncClient() as client:
        client.base_url = os.getenv("AUTH_BASE_URL")
        app_id = request.headers.get("x-APP-ID")
        x_api_token = request.headers.get("X-Develoer-Token")
        response = await client.get(
            f"app/validate-app/{app_id}", headers={"x-api-token": x_api_token}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        key = f"app_{app_id}{x_api_token}"
        background_tasks.add_task(store_developer_data, key, app_id)
        return {"app_id": app_id, "developer_token": x_api_token}


async def validate_user(request: Request, background_tasks: BackgroundTasks):
    async with httpx.AsyncClient() as client:
        client.base_url = os.getenv("AUTH_BASE_URL")
        user_id = request.headers.get("X-User-ID")
        app_id = request.headers.get("X-App-ID")
        x_api_token = request.headers.get("X-Token-ID")
        headers_user = {
            "x-api-token": x_api_token,
            "x-app-id": app_id,
        }
        response = await client.get(
            f"user/validate-user/{user_id}", headers=headers_user
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unauthorized",
            )
        key = f"user_{user_id}{app_id}"
        background_tasks.add_task(store_user_data, key, user_id)
        return {"user_id": user_id, "app_id": app_id}
