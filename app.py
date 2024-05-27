from datetime import datetime
from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    Header,
    Request,
    Depends,
    UploadFile,
    # requests,
    status,
)
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import httpx
import uvicorn
import requests

app = FastAPI()

# Підключення папки зі статичними файлами (стилі, скрипти)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Підключення папки з шаблонами Jinja2
templates = Jinja2Templates(directory="templates")

# base_url = "https://photoshare-python-back.onrender.com/api"
base_url = "http://localhost:8000/api"

app.add_middleware(SessionMiddleware, secret_key="your_secret_key")


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

            # ACCESS_TOKEN = tokens["access_token"]
            request.session["access_token"] = tokens["access_token"]

            return templates.TemplateResponse(
                "login_success.html", {"request": request}
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


@app.get("/contacts", response_class=HTMLResponse)
async def search_contacts(request: Request, limit: int = 10, offset: int = 0):
    access_token = request.session.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token missing or invalid",
        )

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response_contacts = await client.get(
                f"{base_url}/users/all",
                headers=headers,
                params={"limit": limit, "offset": offset},
                follow_redirects=True,
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


@app.get("/contact", response_class=HTMLResponse)
async def search_contacts(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token missing or invalid",
        )

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response_contacts = await client.get(
                f"{base_url}/users/me",
                headers=headers,
                # params={"limit": limit, "offset": offset},
                follow_redirects=True,
            )
            response_contacts.raise_for_status()
            contact = response_contacts.json()

            return templates.TemplateResponse(
                "contact.html", {"request": request, "contact": contact}
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


@app.get("/edit_contact", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("/edit_contact.html", {"request": request})


@app.post("/edit_contact", response_class=HTMLResponse)
async def search_contacts(
    request: Request,
    username: str = Form(...),
    phone: str = Form(...),
    birthday: str = Form(...),
):
    try:
        # Validate birthday format
        birthday_date = datetime.strptime(birthday, "%Y-%m-%d").date()

        # Create the payload
        data = {
            "username": username,
            "phone": phone,
            "birthday": birthday_date.isoformat(),
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {e}",
        )
    access_token = request.session.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token missing or invalid",
        )

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response_contact = await client.put(
                f"{base_url}/users", headers=headers, json=data, follow_redirects=True
            )
            response_contact.raise_for_status()
            contact = response_contact.json()

            return templates.TemplateResponse(
                "contact.html", {"request": request, "contact": contact}
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


@app.get("/upload_photo", response_class=HTMLResponse)
async def upload_photo_form(request: Request):
    return templates.TemplateResponse("upload_photo.html", {"request": request})


@app.post("/upload_photo", response_class=HTMLResponse)
async def upload_photo(
    request: Request,
    photo: UploadFile = File(...),
    description: str = Form(...),
    tags: str = Form(...),
):
    access_token = request.session.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token missing or invalid")

    # tags_list = tags.split(",")

    async with httpx.AsyncClient() as client:

        form_data = {
            "description": description,
            "tags": tags,
        }

        files = {"file": (photo.filename, photo.file, photo.content_type)}

        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.post(
            f"{base_url}/photos",
            headers=headers,
            files=files,
            data=form_data
        )

        
        response.raise_for_status()

    return templates.TemplateResponse("upload_success.html", {"request": request})


@app.get("/photos", response_class=HTMLResponse)
async def search_contacts(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token missing or invalid",
        )

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response_contacts = await client.get(
                f"{base_url}/photos",
                headers=headers,
                # params={"limit": limit, "offset": offset},
                follow_redirects=True,
            )
            response_contacts.raise_for_status()
            photos = response_contacts.json()

            return templates.TemplateResponse(
                "photos.html", {"request": request, "photos": photos}
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
