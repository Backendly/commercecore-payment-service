from fastapi.requests import Request
from fastapi import requests
import httpx
from fastapi import HTTPException, status


async def validate_developer(request: Request):
    async with httpx.AsyncClient() as client:
        client.base_url = "http://127.0.0.1:8080/api/v1/"
        headers = {"Authorization": request.headers.get("Authorization")}
        params = {}
        if request.query_params.get("app_id"):
            params["app_id"] = request.query_params.get("app_id")
        response = await client.get(
            "confirm/developer/", headers=headers, params=params
        )
        response = await client.get("confirm/developer/", headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        return response.json()


async def validate_user(request: Request):
    async with httpx.AsyncClient() as client:
        client.base_url = "http://127.0.0.1:8080/api/v1/"
        headers = {"Authorization": request.headers.get("Authorization")}
        params = {}
        if request.query_params.get("app_id"):
            params["app_id"] = request.query_params.get("app_id")
        response = await client.get("confirm/user/", headers=headers, params=params)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        return response.json()
