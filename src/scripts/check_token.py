import sys
sys.path.append('.')
from interface.alipan import alipan
from interface.sqlite_db import get_access_token, insert, cursor, users_fields, tokens_fields
from functools import partial
from utils.dict import mutl_dict_getter
from utils.time import iso8601str, str2iso
from datetime import timedelta, datetime

if __name__ == '__main__':
    print = partial(print, flush=True, end='\n---------------------------\n')
    print("check if has valid token")
    token = get_access_token()
    is_valid = token and str2iso(token[-2]) > datetime.now() - timedelta(days=90)
    if token and is_valid:
        print("has valid token, skip")
        exit(0)
    print(
        "no valid token, now click this url to get alipan code(授权码) to continue\n",
        alipan.local_authorized_url
    )
    code = input()
    print(f"input code: {code}")
    ret = alipan.get_access_token(code)
    if not ret.get('access_token', None):
        print("get access token failed, please try again")
        print(ret)
        exit(1)
    access_token, refresh_token = ret['access_token'], ret['refresh_token']
    print("get access token success")
    ret = alipan.get_drive_info(access_token)
    if not ret.get('backup_drive_id', None):
        print("get drive info failed, please try again")
        print(ret)
        exit(1)
    user = cursor.execute(
        '''
            select * from users where backup_drive_id = ? limit 1
        ''', (ret['backup_drive_id'],)
    ).fetchone()
    if not user:
        fields = users_fields[1:]
        values = mutl_dict_getter(fields, ret)
        insert('users', values, fields)
    _token = cursor.execute(
        '''
            select * from tokens where user_id = ? limit 1
        ''', (ret['user_id'],)
    ).fetchone()
    if not _token:
        fields = tokens_fields
        values = mutl_dict_getter(fields, {**ret, "access_token": access_token, "refresh_token": refresh_token})
        print(values)
        insert('tokens', values, fields)
    else:
        cursor.execute(
            '''
                update tokens set access_token = ?, refresh_token = ?, updated_at = ? where user_id = ?
            ''', (access_token, refresh_token, iso8601str(), ret['user_id'])
        )
    print("add token success")
