from datetime import datetime

def iso2str(dt: datetime = datetime.now()) -> str:
    '''北京时间, 返回格式为 ISO8601 YYYY-MM-DDTHH:MM:SS+08:00'''
    return dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")

iso8601str = iso2str

def str2iso(s: str) -> datetime:
    '''传入格式为 YYYY-MM-DDTHH:MM:SS+08:00, 返回 datetime'''
    if not s:
        raise ValueError('s is required')
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S+08:00")

def date2str(dt: datetime = datetime.now()) -> str:
    '''北京时间, 返回格式为 YYYY-MM-DD'''
    return dt.strftime("%Y-%m-%d")
