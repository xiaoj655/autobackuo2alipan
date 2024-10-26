from fastapi import FastAPI, Query, BackgroundTasks, Cookie
from fastapi.responses import RedirectResponse, JSONResponse
import uvicorn
import yaml
from utils.dict import mutl_dict_getter, dict_zipper
from interface.alipan import alipan
from interface.sqlite_db import cursor, users_fields, conn, tokens_fields
import logging
from datetime import datetime, timedelta, timezone
from utils.secret import generate_secret_key
import http.cookies
from typing import Literal, override
from email.utils import format_datetime

with open('config/global.yml', 'r') as f:
    config = yaml.safe_load(f)
    web = config['web']

app = FastAPI()
logger = logging.getLogger(__name__)
sessions = set()

class Resp(JSONResponse):
    def __init__(
        self,
        code: int | str = 200,
        data: dict[str, str] | list[dict[str, str]] | None = None,
        detail: str = '',
        background: BackgroundTasks = None
    ):
        super().__init__(content={'code': code, 'data': data, 'detail': detail}, background=background)
    
    @override
    def set_cookie(
        self,
        key: str,
        value: str = "",
        max_age: int | None = None,
        expires: datetime | str | int | None = None,
        path: str | None = "/",
        domain: str | None = None,
        secure: bool = False,
        httponly: bool = False,
        samesite: Literal["lax", "strict", "none"] | None = "lax",
    ) -> None:
        cookie: http.cookies.BaseCookie[str] = http.cookies.SimpleCookie()
        cookie[key] = value
        if max_age is not None:
            cookie[key]["max-age"] = max_age
        if expires is not None:
            if isinstance(expires, datetime):
                cookie[key]["expires"] = format_datetime(expires, usegmt=True)
            else:
                cookie[key]["expires"] = expires
        if path is not None:
            cookie[key]["path"] = path
        if domain is not None:
            cookie[key]["domain"] = domain
        if secure:
            cookie[key]["secure"] = True
        if httponly:
            cookie[key]["httponly"] = True
        if samesite is not None:
            assert samesite.lower() in [
                "strict",
                "lax",
                "none",
            ], "samesite must be either 'strict', 'lax' or 'none'"
            cookie[key]["samesite"] = samesite
        cookie_val = cookie.output(header="").strip()
        self.raw_headers.append((b"set-cookie", cookie_val.encode("latin-1")))
        return self

@app.get('/')
def index():
    return {'message': 'Hello, World!'}

@app.get('/callback', response_class=Resp)
async def callback(code: str = Query(...)):
    try:
        token = alipan.get_access_token(code=code)
        if token.get("access_token", None) is None:
            return Resp(detail="get access token from alipan failed, check your code", code=400)
        access_token, refresh_token = token['access_token'], token['refresh_token']
        user_info = alipan.get_drive_info(access_token)
        user_id = user_info['user_id']

        # update or insert tokens
        ret = cursor.execute("select * from tokens where user_id = ?", (user_id,)).fetchone()
        if not ret:
            cursor.execute("insert into tokens ({}) values ({})".format(
                ', '.join(tokens_fields),
                ', '.join(['?'] * len(tokens_fields))
            ), mutl_dict_getter(tokens_fields, token, user_info))
        else:
            cursor.execute("update tokens set ({}) values ({}) where user_id = ?".format(
                ', '.join(tokens_fields),
                ', '.join(['?'] * len(tokens_fields))
            ), mutl_dict_getter(tokens_fields, token, user_info))
        conn.commit()

        ret = cursor.execute("select * from users where user_id = ?", (user_id,)).fetchone()
        if not ret:
            fields = [f for f in users_fields if f != 'id']
            cursor.execute("insert into users ({}) values ({})".format(
                ', '.join(fields),
                ', '.join(['?'] * len(fields))
            ), mutl_dict_getter(fields, user_info, token))
            conn.commit()
            ret = cursor.execute("select * from users where user_id = ?", (user_id,)).fetchone()
        return Resp(data=dict_zipper(users_fields, ret))
    except Exception as e:
        logger.error(e, exc_info=e)
        return Resp(detail=str(e), code=500)


# 修改了 fastapi 的 Response.set_cookie 方法，使其返回本身
@app.get('/login')
def login(password: str = Query(...), sessionid: str = Cookie(None)):
    if password != web['page_password']:
        return Resp(detail="password is incorrect", code=401) \
            .set_cookie(key="password", value=password, path="/", expires=datetime.now(tz=timezone.utc) - timedelta(days=30))

    if sessionid in sessions:
        sessions.remove(sessionid)
    session_id = generate_secret_key(64)
    sessions.add(session_id)
    return Resp(data="login success").set_cookie(key="sessionid", value=session_id, path="/", expires=datetime.now(tz=timezone.utc) + timedelta(days=7))


if __name__ == '__main__':
    uvicorn.run("main:app", host=web['host'], port=web['port'], reload=web['debug'])
