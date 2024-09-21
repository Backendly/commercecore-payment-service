from fastapi.requests import Request
import httpx
from fastapi import HTTPException, status, BackgroundTasks


from backgrounds import store_user_data, store_developer_data


async def validate_developer(request: Request, background_tasks: BackgroundTasks):
    async with httpx.AsyncClient() as client:
        client.base_url = "https://mock-auth.onrender.com/api/v1/"
        developer_token = request.headers.get("X-Developer-Token")
        app_id = request.headers.get("X-APP-ID")
        headers_developer = {}
        if developer_token:
            headers_developer["Authorization"] = f"Bearer {developer_token}"
        else:
            raise HTTPException(401, detail="Unauthorized")

        if app_id:
            headers_developer["X-App-ID"] = app_id

        response = await client.get("confirm/developer/", headers=headers_developer)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        data = response.json()
        key = f"dev_{developer_token}{app_id}" if app_id else f"dev_{developer_token}"
        background_tasks.add_task(store_developer_data, key, data.get("developer_id"))
        return data


async def validate_user(request: Request, background_tasks: BackgroundTasks):
    async with httpx.AsyncClient() as client:
        client.base_url = "https://mock-auth.onrender.com/api/v1/"
        user_id = request.headers.get("X-User-ID")
        app_id = request.headers.get("X-App-ID")
        headers_user = {}
        if user_id:
            headers_user["X-User-ID"] = user_id
        else:
            raise HTTPException(
                401,
                detail="Please provide a valid user id",
            )
        if app_id:
            headers_user["X-App-ID"] = request.headers.get("X-App-ID")
        response = await client.get("confirm/user/", headers=headers_user)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unauthorized",
            )
        data = response.json()
        key = f"usr_{user_id}{app_id}" if app_id else f"usr_{user_id}"
        background_tasks.add_task(store_user_data, key, data.get("user_id"))
        return data
