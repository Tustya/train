import base64
import hashlib
import hmac
import json
from typing import Optional
from fastapi import FastAPI, Form, Cookie
from fastapi.responses import Response


app = FastAPI()

SECRET_KEY = "hlkjh253l4kjh324l5h3l45hj34g5hk3j4hg5kj34hg5k"
PASSWORD_SALT = "kjhldkfgjheg876g98fsd568765f87as6d5f87asdf8"

users : dict[str, dict[str, str | int | float]] = {
    '1': {
        "username": "1",
        "password": "56aea0d7445fa40dd5b3f8a3ad5dfffd31a629089a4b2ab5edcc59bac0ff75f9",
        "balance": 100_00,
    }
}

def sign_data(data: str) -> str:
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
        ).hexdigest().upper()

def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_b64, sign = username_signed.split(".")
    username = base64.b64decode(username_b64.encode()).decode()
    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username

def verify_password(username: str, password: str) -> bool:
    password_hash = hashlib.sha256( (password + PASSWORD_SALT).encode() ).hexdigest().lower()
    stored_password_hash = users[username]["password"].lower()
    return password_hash == stored_password_hash




@app.get("/")
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('templates/login.html', 'r') as f:
        login_page = f.read()

    if not username:
        return Response(login_page, media_type="text/html")
    
    valid_username = get_username_from_signed_string(username)
    if not valid_username:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie()
        return response

    response = Response((f"Hi, {users[valid_username]['username']}!<br>Balance: {users[valid_username]['balance']}"), media_type="text/html")
    return response
    
    


@app.post("/login")
def process_login_page(username: str = Form(...), password: str = Form(...)):
    user = users.get(username)
    if not user or not verify_password(username, password):
        return Response(
                json.dumps({
                    "succes": False,
                    "message": "я вас не знаю"
                }), 
                media_type="application/json"
                )
    response =  Response(json.dumps({
        "success": True,
        "message": f"Hi!<br>Balance: {user['balance']}"
    }), media_type='application/json')
    username_signed = base64.b64encode(username.encode()).decode() + "." + sign_data(username)
    response.set_cookie(key="username", value=username_signed)
    return response