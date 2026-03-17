from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Form, HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/css", StaticFiles(directory="css"), name="css")

import gspread
from google.oauth2.service_account import Credentials

def connect_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=scopes
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open("FASTAPI")
    sheet = spreadsheet.worksheet("sheet1")

    return sheet

@app.get("/sheet")
def read_sheet():
    sheet = connect_sheet()
    data = sheet.get_all_records()
    return data

@app.get("/")
def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    tel: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    # 🔒 1. Check password match
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    sheet = connect_sheet()

    # 📊 2. Get existing users
    records = sheet.get_all_records()

    # 🚫 3. Check duplicate email
    for user in records:
        if user["email"] == email:
            raise HTTPException(status_code=400, detail="Email already registered")

    # 🔐 4. Hash password
    hashed_password = pwd_context.hash(password)

    # 📝 5. Save to Google Sheets
    sheet.append_row([username, email, tel, hashed_password])

    # ✅ 6. Success response
    return {
        "message": "User registered successfully 🎉",
        "username": username,
        "email": email
    }

@app.get("/example")
def ex(request: Request):
    return templates.TemplateResponse("example.html", {"request": request})


