from dataclasses import dataclass, field
from urllib.parse import quote
from yaml import Loader, load
import requests
from typing import Annotated

@dataclass(frozen=True)
class Alipan:
    scope:              str
    appid:              str
    secret:             str
    oauth_redirect_uri: str
    baseurl:            str = field(default="https://openapi.alipan.com", repr=False)

    @property
    def authorized_url(self) -> str:
        return self.baseurl + \
            f"/oauth/authorize?client_id={self.appid}&redirect_uri={quote(self.oauth_redirect_uri, safe="")}&scope={self.scope}&response_type=code"
    @property
    def local_authorized_url(self) -> str:
        return self.baseurl + \
            f"/oauth/authorize?client_id={self.appid}&redirect_uri=oob&scope={self.scope}&response_type=code"
    
    def auth_header(self, access_token:str, header: dict = {}):
        header.update({"Authorization": f"Bearer {access_token}"})
        return header
    
    def get_access_token(
            self, code: str | None = None, 
            refresh_token: str | None = None
        ) -> dict:

        if not code and not refresh_token:
            raise Exception("code and refresh is all empty")

        url = self.baseurl + "/oauth/access_token"
        data = {
            "client_id": self.appid,
            "client_secret": self.secret,
        }

        if code:
            data.update({"grant_type": "authorization_code", "code": code})
        else:
            data.update({"grant_type": "refresh_token", "refresh_token": refresh_token})

        ret = requests.post(url, json=data).json()
        return ret
    
    def get_drive_info(self, access_token: str):
        url = self.baseurl + "/adrive/v1.0/user/getDriveInfo"
        ret = requests.post(url=url, headers=self.auth_header(access_token)).json()
        return ret
    
    def get_file_list(self, access_token: str, **kwargs):
        url = self.baseurl + "/adrive/v1.0/openFile/list"
        print(kwargs)
        return requests.post(url, json=kwargs, headers=self.auth_header(access_token)).json()
    
    def create_file(self, access_token: str, **kwargs):
        url = self.baseurl + "/adrive/v1.0/openFile/create"
        return requests.post(url, json=kwargs, headers=self.auth_header(access_token)).json()
    
    def upload_file(self,
                    upload_url: Annotated[str, "oss url, use put http method, get from 'self.create_file'"],
                    file_path: str
                    ):
        with open(file_path, 'rb') as f:
            ret = requests.put(upload_url, data=f)
        return ret.text
    
    def refresh_upload_url(self,access_token: str, **kwargs):
        url = self.baseurl + "/adrive/v1.0/openFile/getUploadUrl"
        return requests.post(url, json=kwargs, headers=self.auth_header(access_token))
    
    def complete_upload(self, access_token: str, **kwargs):
        url = self.baseurl + "/adrive/v1.0/openFile/complete"
        return requests.post(url, json=kwargs, headers=self.auth_header(access_token))
    
    def one_call_upload(
        self,
        access_token: str,
        drive_id: str,
        parent_file_id: str,
        name: str,
        local_file_path: str,
        check_name_mode: str = 'auto_rename',
        ):
        ret = self.create_file(
            access_token,
            drive_id=drive_id,
            type='file',
            name=name,
            check_name_mode=check_name_mode,
            parent_file_id=parent_file_id
        )
        oss_url = ret['part_info_list'][0]['upload_url']
        upload_id, file_id = ret['upload_id'], ret['file_id']
        ret = self.upload_file(oss_url, local_file_path)
        print(ret)
        ret = self.complete_upload(access_token, file_id=file_id, upload_id=upload_id, drive_id=drive_id)
        print(ret)
        return ret

with open("config/global.yml", 'r') as f:
    c = load(f, Loader=Loader)
    c = c['alipan']


code = "ea81845793a541fc85749c5db524151c"
access_token = "eyJraWQiOiJLcU8iLCJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxZGNiNTU3YTdkMTc0NmFmYWZkMTcwODEyNGRhMWZhYiIsImF1ZCI6IjgzZjQ3NjZiNDZiODQwNjI5NmI2Yjg4MDY1YjRhZDAyIiwicyI6ImNkYSIsImQiOiIzNTY4NTEzOTEsMzU4MDM3MTIzIiwiaXNzIjoiYWxpcGFuIiwiZXhwIjoxNzI5NzI5OTM5LCJpYXQiOjE3Mjk3MjI3MzYsImp0aSI6IjAyNzU4NjdhMDQ1MzRhN2JiMDdkYmU1MWVhMzEzNDAxIn0.9cnRWV4eKOxPt8so4Mf_18H-xWKOLAmrLQ0XLGHvuFs"
drive_id = "356851391"
resource_drive_id = "358037123"

alipan = Alipan(**c)
# print(alipan.get_driver_info(access_token=access_token))
# print(alipan.get_file_list(access_token=access_token, drive_id=drive_id, parent_file_id="root"))
