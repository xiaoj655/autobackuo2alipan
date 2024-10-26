import sqlite3 as sqlite

try:
    conn = sqlite.connect('dbname.db')
except Exception as e:
    print(e)

cursor = conn.cursor()

users_fields = [
    "id",
    "user_id",
    "resource_drive_id",
    "name",
    "avatar",
    "nick_name",
    "default_drive_id",
    "backup_drive_id",
    "created_at",
    "updated_at"
]

tokens_fields = [
    "user_id",
    "access_token",
    "refresh_token",
    "updated_at",
    "created_at"
]

backup_log_fields = [
    "id",
    "label",
    "created_at",
    "source",
    "compress_type",
    "output",
    "status",
    "source_type",
    "source_size",
    "compress_size",
]

def setup_sqlite(cursor: sqlite.Cursor, conn: sqlite.Connection):
    cursor.execute('''
    create table if not exists users (
                    id integer primary key autoincrement,
                    user_id text not null,
                    backup_drive_id text not null,
                    default_drive_id text default '',
                    resource_drive_id text default '',
                    name text default '',
                    avatar text default '',
                    nick_name text default '',
                    created_at text default "1900-01-01T00:00:00+08:00",
                    updated_at text default "1900-01-01T00:00:00+08:00"
                )
    ''')
    cursor.execute('''
        create table if not exists tokens (
                    user_id text not null,
                    access_token text default '',
                    refresh_token text default '',
                    updated_at text default "1900-01-01T00:00:00+08:00",
                    created_at text default "1900-01-01T00:00:00+08:00"
                    )
    ''')
    cursor.execute('''
        create table if not exists backup_log (
            id integer primary key autoincrement,
            label text not null,
            created_at text default "1900-01-01T00:00:00+08:00",
            cloud_status text default '待上传',
            md5 text default '',
            source text not null,
            compress_type text not null,
            output text not null,
            status text default '',
            source_type text default '',
            source_size text default '',
            compress_size text default ''
        )
    ''')
    conn.commit()

def insert(
    db: str,
    values: tuple[str],
    value_names: tuple[str] = None,
    cursor: sqlite.Cursor = cursor,
    conn: sqlite.Connection = conn
):
    cursor.execute(f"insert into {db} ({','.join(value_names)}) values ({','.join(['?'] * len(values))})", values)
    conn.commit()

def select(
    db: str,
    value_names: tuple[str] = None,
    cursor: sqlite.Cursor = cursor,
):
    cursor.execute(f"select {','.join(value_names)} from {db}")
    return cursor.fetchall()

def select_by_user_id(
    user_id: str,
    db: str = 'users',
    value_names: tuple[str] = users_fields,
    cursor: sqlite.Cursor = cursor,
):
    cursor.execute(f"select {','.join(value_names)} from {db} where user_id = ?", (user_id,))
    return cursor.fetchall()

def select_latest_backup_log(
    label: str,
    cursor: sqlite.Cursor = cursor,
):
    cursor.execute('''
        select * from backup_log
        where label = ?
        order by created_at desc
        limit 1
    ''', (label,))
    return cursor.fetchone()

def insert_backup_log(
    label: str,
    source: str,
    compress_type: str,
    output: str,
    cursor: sqlite.Cursor = cursor,
    conn: sqlite.Connection = conn
):
    # insert('backup_log', (label, source, compress_type, output), backup_log_fields, cursor, conn)
    pass

def get_access_token(
    user_id: str | None = None,
    cursor: sqlite.Cursor = cursor,
):
    if user_id:
        pass
    else:
        cursor.execute('''
            select * from tokens
            order by updated_at desc
            limit 1
        ''')
    return cursor.fetchone()

setup_sqlite(cursor, conn)

if __name__ == '__main__':
    test_backup_log = (
        "Test Backup",  # label
        "2023-05-15T14:30:00+08:00",  # created_at
        "/path/to/source/file.zip",  # source
        "zip",  # compress_type
        "/path/to/output/backup.zip",  # output
        "completed",  # status
        "file",  # source_type
        "1024MB",  # source_size
        "512MB"  # compress_size
    )
