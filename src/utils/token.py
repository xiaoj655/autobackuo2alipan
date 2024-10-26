from interface.alipan import alipan
from utils.time import str2iso, iso2str
from interface.sqlite_db import cursor, conn
from datetime import timedelta, datetime

def get_valid_token(user_id: str | None = None):
    token = cursor.execute(
        '''
            select * from tokens where user_id = ? order by updated_at desc limit 1
        ''', (user_id,)
    ).fetchone()
    if not token or str2iso(token[-2]) < datetime.now() - timedelta(days=90):
        return None
    is_valid = str2iso(token[-2]) > datetime.now() - timedelta(seconds=7200)
    if not is_valid:
        ret = alipan.refresh_access_token(token[-3])
        cursor.execute(
            '''
                update tokens set access_token = ?, refresh_token = ?, updated_at = ? where user_id = ?
            ''', (ret['access_token'], ret['refresh_token'], iso2str(), token[0])
        )
        conn.commit()
        return ret['access_token']

    return token[1]

if __name__ == '__main__':
    print(get_valid_token())