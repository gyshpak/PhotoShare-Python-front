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
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import httpx
import uvicorn
import requests
import base64

app = FastAPI()

# Підключення папки зі статичними файлами (стилі, скрипти)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Підключення папки з шаблонами Jinja2
templates = Jinja2Templates(directory="templates")

base_url = "https://photoshare-python-back.onrender.com/api"
# base_url = "http://localhost:8000/api"
# base_url = "https://photoshare-python-back-48d1.onrender.com/api"

app.add_middleware(SessionMiddleware, secret_key="your_secret_key")


class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            response = await call_next(request)
            return response
        except httpx.ReadTimeout:
            return templates.TemplateResponse(
                # "Timeout.html", {"request": request, "message": "The request timed out. Please try again later."}
                "Timeout.html", {"request": request}
            )

app.add_middleware(TimeoutMiddleware)

def base64encode(value: bytes) -> str:
    return base64.b64encode(value).decode("utf-8")

templates.env.filters["b64encode"] = base64encode


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

            request.session["access_token"] = tokens["access_token"]

            return templates.TemplateResponse(
                "login_success.html", {"request": request}
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                error_detail = e.response.json().get("detail", "Unauthorized")
                if error_detail == "User is banned":
                    return templates.TemplateResponse(
                        "user_banned.html", {"request": request}
                    )
                elif error_detail == "Email not confirmed":
                    return templates.TemplateResponse(
                        "email_not_confirmed.html", {"request": request}
                    )
                elif error_detail == "Invalid email" or error_detail == "Invalid password":
                    return templates.TemplateResponse(
                        "login_failure.html", {"request": request}
                    )
                else:
                    return templates.TemplateResponse(
                        "Unauthorized.html", {"request": request}
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users: {e}",
                )

# Функція виходу користувача
@app.get("/logout", response_class=HTMLResponse)
async def login_user(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Access token missing or invalid",
        # )
        return templates.TemplateResponse(
                    "access_denied.html", {"request": request}
                )
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response_users = await client.post(
                f"{base_url}/auth/logout",
                headers=headers,
                follow_redirects=True,
            )
            request.session["access_token"] = None
            response_users.raise_for_status()
            users = response_users.json()

            return templates.TemplateResponse(
                "logout.html", {"request": request}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return templates.TemplateResponse(
                    "Unauthorized.html", {"request": request}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users: {e}",
                )

# Функція пошуку користувача
@app.get("/users", response_class=HTMLResponse)
async def search_users(request: Request, limit: int = 10, offset: int = 0):
    access_token = request.session.get("access_token")
    if not access_token:
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Access token missing or invalid",
        # )
        return templates.TemplateResponse(
                    "access_denied.html", {"request": request}
                )

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response_users = await client.get(
                f"{base_url}/users/all",
                headers=headers,
                params={"limit": limit, "offset": offset},
                follow_redirects=True,
            )
            response_users.raise_for_status()
            users = response_users.json()

            return templates.TemplateResponse(
                "users.html", {"request": request, "users": users}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return templates.TemplateResponse(
                    "access_denied.html", {"request": request}
                )
            if e.response.status_code == 403:
                return templates.TemplateResponse(
                    "only_admin.html", {"request": request}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users: {e}",
                )

# Функція перегляду користувача
@app.get("/user", response_class=HTMLResponse)
async def search_users(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Access token missing or invalid",
        # )
        return templates.TemplateResponse(
                    "access_denied.html", {"request": request}
                )

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response_users = await client.get(
                f"{base_url}/users/me",
                headers=headers,
                # params={"limit": limit, "offset": offset},
                follow_redirects=True,
            )
            response_users.raise_for_status()
            user = response_users.json()

            return templates.TemplateResponse(
                "user.html", {"request": request, "user": user}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return templates.TemplateResponse(
                    "access_denied.html", {"request": request}
                )
            if e.response.status_code == 429:
                return templates.TemplateResponse(
                    "suspicious_activity.html", {"request": request}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users: {e}",
                )

# Функція редагування користувача
@app.get("/edit_user", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("/edit_user.html", {"request": request})

# Функція редагування користувача
@app.post("/edit_user", response_class=HTMLResponse)
async def search_users(
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
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Access token missing or invalid",
        # )
        return templates.TemplateResponse(
                    "access_denied.html", {"request": request}
                )

    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response_user = await client.put(
                f"{base_url}/users", headers=headers, json=data, follow_redirects=True
            )
            response_user.raise_for_status()
            user = response_user.json()

            return templates.TemplateResponse(
                "user.html", {"request": request, "user": user}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return templates.TemplateResponse(
                    "Unauthorized.html", {"request": request}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch users: {e}",
                )

# Функція оновлення аватара
@app.get("/update_avatar", response_class=HTMLResponse)
async def upload_photo_form(request: Request):
    return templates.TemplateResponse("update_avatar.html", {"request": request})

# Функція оновлення аватара
@app.post("/update_avatar", response_class=HTMLResponse)
async def upload_photo(
    request: Request,
    photo: UploadFile = File(...),
):
    access_token = request.session.get("access_token")
    if not access_token:
        # raise HTTPException(status_code=401, detail="Access token missing or invalid")
        return templates.TemplateResponse(
                    "access_denied.html", {"request": request}
                )

    async with httpx.AsyncClient() as client:
        files = {"file": (photo.filename, photo.file, photo.content_type)}
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.put(
            f"{base_url}/users/avatar",
            headers=headers,
            files=files,
        )
        response.raise_for_status()
    return templates.TemplateResponse(
        "upload_avatar_success.html", {"request": request}
    )

# Функція оновлення ролі
@app.post("/role", response_class=HTMLResponse)
async def change_role(request: Request, user_id: str = Form(...), role: str = Form(...)):
    access_token = request.session.get("access_token")
    if not access_token:
        # raise HTTPException(status_code=401, detail="Access token missing or invalid")
        return templates.TemplateResponse(
                    "access_denied.html", {"request": request}
                )
    
    async with httpx.AsyncClient() as client:
        form_data = {
            "role": role,
        }

        # headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.put(
            f"{base_url}/users/role/{user_id}",
            headers=headers,
            #json=role
            data=form_data
        )
        response.raise_for_status()
    return RedirectResponse(url="/users", status_code=303)
    #return templates.TemplateResponse("users.html", {"request": request})

# Функція блокування користувача
@app.post("/ban", response_class=HTMLResponse)
async def change_role(request: Request, user_id: int = Form(...), isbanned: str = Form(...)):
    access_token = request.session.get("access_token")
    if not access_token:
        # raise HTTPException(status_code=401, detail="Access token missing or invalid")
        return templates.TemplateResponse(
                    "access_denied.html", {"request": request}
                )
    
    async with httpx.AsyncClient() as client:
        form_data = {
            "isbanned": isbanned,
        }

        # headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.put(
            f"{base_url}/users/ban/{user_id}",
            headers=headers,
            #json=isbanned
            data=form_data
        )
        response.raise_for_status()
    return RedirectResponse(url="/users", status_code=303)
    #return templates.TemplateResponse("users.html", {"request": request})

# Функція завантаження фото
@app.get("/upload_photo", response_class=HTMLResponse)
async def upload_photo_form(request: Request):
    return templates.TemplateResponse("upload_photo.html", {"request": request})


# # Функція завантаження фото
# @app.post("/upload_photo", response_class=HTMLResponse)
# async def upload_photo(
#     request: Request,
#     photo: UploadFile = File(...),
#     description: str = Form(...),
#     tags: str = Form(...),
# ):
#     access_token = request.session.get("access_token")
#     if not access_token:
#         # raise HTTPException(status_code=401, detail="Access token missing or invalid")
#         return templates.TemplateResponse(
#                     "access_denied.html", {"request": request}
#                 )

#     # tags_list = tags.split(",")

#     async with httpx.AsyncClient() as client:

#         form_data = {
#             "description": description,
#             "tags": tags,
#         }

#         files = {"file": (photo.filename, photo.file, photo.content_type)}

#         headers = {"Authorization": f"Bearer {access_token}"}

#         response = requests.post(
#             f"{base_url}/photos",
#             headers=headers,
#             files=files,
#             data=form_data
#         )

#         response.raise_for_status()

#     return templates.TemplateResponse("upload_success.html", {"request": request})

# # Функція перегляду фото
# @app.get("/photos", response_class=HTMLResponse)
# async def get_photos(request: Request):
#     access_token = request.session.get("access_token")
#     if not access_token:
#         return templates.TemplateResponse(
#                     "access_denied.html", {"request": request}
#                 )
#     async with httpx.AsyncClient() as client:
#         try:
#             headers = {"Authorization": f"Bearer {access_token}"}

#             response = await client.get(
#                 f"{base_url}/photos?limit=50",
#                 headers=headers,
#                 follow_redirects=True,
#             )
#             response.raise_for_status()
#             photos = response.json()

#             for photo in photos:
#                 response_QR = await client.get(
#                     f"{base_url}/photos/link/{photo['id']}",
#                     headers=headers,
#                     follow_redirects=True,
#                 )
#                 response_QR.raise_for_status()
#                 photo["QR_code"] = response_QR.content

#             return templates.TemplateResponse(
#                 "photos.html", {"request": request, "photos": photos}
#             )
#         except httpx.HTTPStatusError as e:
#             if e.response.status_code == 401:
#                 return templates.TemplateResponse(
#                     "Unauthorized.html", {"request": request}
#                 )
#             else:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail=f"Failed to fetch photos: {e}",
#                 )


# # Функція завантаження фото
# @app.post("/upload_photo", response_class=HTMLResponse)
# async def upload_photo(
#     request: Request,
#     photo: UploadFile = File(...),
#     description: str = Form(...),
#     tags: str = Form(...),
# ):
#     access_token = request.session.get("access_token")
#     if not access_token:
#         # raise HTTPException(status_code=401, detail="Access token missing or invalid")
#         return templates.TemplateResponse(
#                     "access_denied.html", {"request": request}
#                 )

#     # tags_list = tags.split(",")

#     async with httpx.AsyncClient() as client:

#         form_data = {
#             "description": description,
#             "tags": tags,
#         }

#         files = {"file": (photo.filename, photo.file, photo.content_type)}

#         headers = {"Authorization": f"Bearer {access_token}"}

#         response = requests.post(
#             f"{base_url}/photos",
#             headers=headers,
#             files=files,
#             data=form_data
#         )

#         response.raise_for_status()

#     return templates.TemplateResponse("upload_success.html", {"request": request})

# Функція перегляду фото
@app.get("/photos", response_class=HTMLResponse)
async def get_photos(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        return templates.TemplateResponse(
                    "access_denied.html", {"request": request}
                )
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response = await client.get(
                f"{base_url}/photos?limit=50",
                headers=headers,
                follow_redirects=True,
            )
            response.raise_for_status()
            photos = response.json()

            # for photo in photos:
            #     response_QR = await client.get(
            #         f"{base_url}/photos/link/{photo['id']}",
            #         headers=headers,
            #         follow_redirects=True,
            #     )
            #     response_QR.raise_for_status()
            #     photo["QR_code"] = response_QR.content

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
                    detail=f"Failed to fetch photos: {e}",
                )


@app.get("/photo/{photo_id}", response_class=HTMLResponse)
async def get_photo(request: Request, photo_id: str):
    access_token = request.session.get("access_token")
    if not access_token:
        return templates.TemplateResponse("access_denied.html", {"request": request})
    async with httpx.AsyncClient() as client:
        try:
            headers = {"Authorization": f"Bearer {access_token}"}

            response = await client.get(
                f"{base_url}/photos/{photo_id}",
                headers=headers,
                follow_redirects=True,
            )
            response.raise_for_status()
            photo = response.json()
        
            response_QR = await client.get(
                f"{base_url}/photos/link/{photo['id']}",
                headers=headers,
                follow_redirects=True,
            )

            response_QR.raise_for_status()
            photo["QR_code"] = response_QR.content

            return templates.TemplateResponse(
                "photo.html", {"request": request, "photo": photo}
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return templates.TemplateResponse(
                    "Unauthorized.html", {"request": request}
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch photos: {e}",
                )


# Функція додавання комментарів
@app.post("/add_comment", response_class=HTMLResponse)
async def add_comment(
    request: Request, photo_id: str = Form(...), comment: str = Form(...)
):
    access_token = request.session.get("access_token")
    if not access_token:
        # raise HTTPException(status_code=401, detail="Access token missing or invalid")
        return templates.TemplateResponse(
                    "access_denied.html", {"request": request}
                )

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.post(
            f"{base_url}/comments/{photo_id}", headers=headers, json=comment
        )
        response.raise_for_status()

    return RedirectResponse(url=f"/photo/{photo_id}", status_code=303)


# Функція видалення коментарів
@app.post("/delete_comment", response_class=HTMLResponse)
async def delete_comment(
    request: Request, comment_id: str = Form(...), photo_id: str = Form(...)
):
    access_token = request.session.get("access_token")
    if not access_token:
        return templates.TemplateResponse("access_denied.html", {"request": request})

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.delete(
            f"{base_url}/comments/record/{comment_id}", headers=headers
        )
        response.raise_for_status()

    return RedirectResponse(url=f"/photo/{photo_id}", status_code=303)


@app.post("/dell_photo", response_class=HTMLResponse)
async def delete_photo(
    request: Request, photo_id: str = Form(...)
):
    access_token = request.session.get("access_token")
    if not access_token:
        return templates.TemplateResponse("access_denied.html", {"request": request})

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.delete(
            f"{base_url}/photos/{photo_id}", headers=headers
        )
        response.raise_for_status()

    return RedirectResponse(url="/photos", status_code=303)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True, log_level="info")
