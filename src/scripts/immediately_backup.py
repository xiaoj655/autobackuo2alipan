import sys
sys.path.append('.')
from utils.backup import main as backup
from utils.token import get_valid_token
from interface.alipan import alipan
from interface.sqlite_db import select_by_user_id
from datetime import datetime
import os

if __name__ == '__main__':
    user_id = '1dcb557a7d1746afafd1708124da1fab'
    token = get_valid_token(user_id)
    if not token:
        print("no valid token, please add token first")
        exit(1)
    drive_id = select_by_user_id(user_id, value_names=('backup_drive_id',))[0][0]
    print("has valid token, now backup")
    ret = alipan.create_file(token, drive_id=drive_id, type='folder', name='auto_backup', check_name_mode='refuse', parent_file_id='root')

    date_str = datetime.now().strftime('%Y-%m-%d')
    parent_file_id = ret['file_id']
    ret = alipan.create_file(token, drive_id=drive_id, type='folder', name=date_str, check_name_mode='refuse', parent_file_id=parent_file_id)

    parent_file_id = ret['file_id']

    upload_files_dirpath = backup()

    for file in os.listdir(upload_files_dirpath):
        local_file_path = f'{upload_files_dirpath}/{file}'

        ret = alipan.one_call_upload(
            token,
            drive_id,
            parent_file_id,
            file,
            local_file_path
        )
        print(ret)
