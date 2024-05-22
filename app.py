from fastapi import FastAPI, Form, HTTPException, Header, Request, Depends, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
import httpx
import uvicorn

app = FastAPI()

# Підключення папки зі статичними файлами (стилі, скрипти)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Підключення папки з шаблонами Jinja2
templates = Jinja2Templates(directory="templates")

base_url = (
    "https://photoshare-python-back.onrender.com/api"  # URL локального сервера FastAPI
)


ACCESS_TOKEN = None

# Базовий шаблон з кнопками для запуску різних функцій
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


# Функція реєстрації нового користувача
@app.post("/signup")
async def signup_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    data = {
        "username": name,
        "email": email,
        "password": password,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/auth/signup", json=data)
            response.raise_for_status()  # Перевірка статусу відповіді
            response_data = response.json()
            return templates.TemplateResponse(
                "registration_success.html",
                {"request": request, "data": response_data},
            )
            # return {"message": "User registered successfully", "data": response.json()}
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 422:
                error_detail = e.response.json().get("detail", "Unprocessable Entity")
                return templates.TemplateResponse(
                    "registration_failure.html",
                    {"request": request, "error": error_detail},
                )
            return templates.TemplateResponse(
                "registration_failure.html", {"request": request, "error": str(e)}
            )

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Функція входу користувача
@app.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request, name: str = Form(...), password: str = Form(...)
):
    data = {"username": name, "password": password}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/auth/login", data=data)
            response.raise_for_status()
            tokens = response.json()

            # Передача токенів через HTTP заголовок
            ACCESS_TOKEN = tokens["access_token"]
            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
            ##########################
            # Виконати GET запит на /contacts з токеном авторизації
            response_contacts = await client.get(
                f"{base_url}/users/all", headers=headers, follow_redirects=True
            )
            response_contacts.raise_for_status()
            contacts = response_contacts.json()

            return templates.TemplateResponse(
                "contacts.html", {"request": request, "contacts": contacts}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return templates.TemplateResponse(
                    "Unauthorized.html", {"request": request}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch contacts: {e}",
                )


# Функція входу користувача
@app.post("/contacts", response_class=HTMLResponse)
async def search_contacts(
    request: Request, name: str = Form(...), password: str = Form(...)
):
    data = {"username": name, "password": password}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/auth/login", data=data)
            response.raise_for_status()
            tokens = response.json()

            # Передача токенів через HTTP заголовок
            ACCESS_TOKEN = tokens["access_token"]
            headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
            ##########################
            # Виконати GET запит на /contacts з токеном авторизації
            response_contacts = await client.get(
                f"{base_url}/users/all", headers=headers, follow_redirects=True
            )
            response_contacts.raise_for_status()
            contacts = response_contacts.json()

            return templates.TemplateResponse(
                "contacts.html", {"request": request, "contacts": contacts}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return templates.TemplateResponse(
                    "Unauthorized.html", {"request": request}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch contacts: {e}",
                )


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True, log_level="info")


#############################
#     return RedirectResponse(url="/contacts", headers=headers)
#     # return templates.TemplateResponse("login.html",{"request": request, "message": f"Login successful {access_token}"},)
# except httpx.HTTPStatusError as e:
#     return templates.TemplateResponse(
#         "login.html",
#         {"request": request, "error_message": f"Login failed: {e}"},
#     )


# Функція отримання списку контактів
# @app.get("/contacts", response_class=JSONResponse)
# async def get_contacts(request: Request, authorization: str = Header(None)):
#     if not authorization or not authorization.startswith("Bearer "):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authorization header",
#         )

#     access_token = authorization.split(" ")[1]

#     async with httpx.AsyncClient() as client:
#         try:
#             headers = {"Authorization": f"Bearer {access_token}"}
#             response = await client.get(f"{base_url}/contacts/", headers=headers)
#             response.raise_for_status()  # Перевірка статусу відповіді
#             contacts = response.json()

#             return contacts
#             # return templates.TemplateResponse(
#             #     "contacts.html", {"request": request, "contacts": contacts}
#             # )
#         except httpx.HTTPStatusError as e:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail=f"Failed to fetch contacts: {e}",
#             )


# @app.get("/contacts", response_class=HTMLResponse)
# async def get_contacts(authorization: str = Depends()):
#     if not authorization or not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")

#     access_token = authorization.split(" ")[1]

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(f"{base_url}/contacts/")
#             response.raise_for_status()  # Перевірка статусу відповіді
#             return {"message": "Contacts fetched successfully", "data": response.json()}
#         except httpx.HTTPStatusError as e:
#             raise Exception(f"Failed to fetch contacts: {e}")


#     # Тут має бути ваша логіка для використання access_token у запиті до захищеного ендпоінту (наприклад, /contacts)

#     return {"message": "Contacts retrieved successfully"}
