from fastapi.requests import Request
import httpx
from fastapi import HTTPException, status, BackgroundTasks


from backgrounds import store_user_data, store_developer_data


key_developer_1 = "developer_{developer_id}{app_id}{user_id}"
key_user_1 = "user_{developer_id}{app_id}{user_id}"

key_developer_2 = "developer_{developer_id}{app_id}"
key_user_2 = "user_{user_id}{app_id}"

key_developer_3 = "developer_{developer_id}"
key_user_3 = "user_{user_id}"

headers_developer = {}
params_developer = {}

headers_user = {}
params_user = {}


async def validate_developer(request: Request, background_tasks: BackgroundTasks):
    async with httpx.AsyncClient() as client:
        client.base_url = "http://127.0.0.1:8080/api/v1/"
        authorization = request.headers.get("Authorization")
        if authorization:
            headers_developer["Authorization"] = authorization
        elif head_authorization := request.headers.get("X-Developer-Token"):
            headers_developer["Authorization"] = f"Bearer {head_authorization}"
        elif request.headers.get("X-Developer-ID"):
            headers_developer["X-Developer-ID"] = request.headers.get("X-Developer-ID")
        else:
            raise HTTPException(401, detail="Unauthorized")
        if request.query_params.get("app_id"):
            params_developer["app_id"] = request.query_params.get("app_id")
        elif request.headers.get("X-App-ID"):
            headers_developer["X-App-ID"] = request.headers.get("X-App-ID")

        response = await client.get(
            "confirm/developer/", headers=headers_developer, params=params_developer
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        data = response.json()

        formatted_key_developer_2 = key_developer_2.format(
            developer_id=data.get("developer_id"), app_id=params_developer.get("app_id")
        )
        formatted_key_developer_3 = key_developer_3.format(
            developer_id=data.get("developer_id")
        )
        if request.headers.get("X-Developer-Token"):
            background_tasks.add_task(
                store_developer_data,
                request.headers.get("X-Developer-Token"),
                data["developer_id"],
            )
        background_tasks.add_task(
            store_developer_data, formatted_key_developer_3, data["developer_id"]
        )
        background_tasks.add_task(
            store_developer_data, formatted_key_developer_2, data["developer_id"]
        )
        return data


async def validate_user(request: Request, background_tasks: BackgroundTasks):
    async with httpx.AsyncClient() as client:
        client.base_url = "http://127.0.0.1:8080/api/v1/"
        authorization = request.headers.get("Authorization")
        if authorization:
            headers_user["Authorization"] = authorization
        elif head_authorization := request.headers.get("X-User-Token"):
            headers_user["Authorization"] = f"Bearer {head_authorization}"
        elif request.headers.get("X-User-ID"):
            headers_user["X-User-ID"] = request.headers.get("X-User-ID")
        else:
            raise HTTPException(
                401,
                detail="Please provide a valid user token, id or authorization header",
            )
        if request.query_params.get("app_id"):
            params_user["app_id"] = request.query_params.get("app_id")
        elif request.headers.get("X-App-ID"):
            headers_user["X-App-ID"] = request.headers.get("X-App-ID")
        response = await client.get(
            "confirm/user/", headers=headers_user, params=params_user
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unauthorized, {response.json().get('message')}",
            )
        data = response.json()
        formatted_key_developer_1 = key_developer_1.format(
            developer_id=headers_developer.get("X-Developer-ID"),
            app_id=params_user.get("app_id"),
            user_id=data.get("user_id"),
        )
        formatted_key_user_1 = key_user_1.format(
            developer_id=headers_developer.get("X-Developer-ID"),
            app_id=params_user.get("app_id"),
            user_id=data.get("user_id"),
        )
        formatted_key_user_2 = key_user_2.format(
            user_id=data.get("user_id"),
            app_id=data.get("app_id"),
        )
        formatted_key_user_3 = key_user_3.format(user_id=data.get("user_id"))

        background_tasks.add_task(
            store_user_data, formatted_key_user_3, data["user_id"]
        )
        background_tasks.add_task(
            store_user_data, formatted_key_user_2, data["user_id"]
        )
        background_tasks.add_task(
            store_user_data, formatted_key_user_1, data["user_id"]
        )
        background_tasks.add_task(
            store_user_data,
            formatted_key_developer_1,
            headers_developer.get("X-Developer-ID"),
        )
        return data
