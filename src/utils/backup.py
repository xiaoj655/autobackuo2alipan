import sys
sys.path.append(".")
import os,logging, subprocess
from utils.time import date2str, iso2str
from interface.sqlite_db import insert, backup_log_fields
import yaml
from typing import Annotated

logger = logging.getLogger(__name__)
accept_compress_type = ['.tar.gz', '.zip', '.tar']
temp_path = '/tmp/backup2alipan'
backup_path = '/var/backup/data2alipan'

if not os.path.exists(temp_path):
    os.makedirs(temp_path, exist_ok=True)
if not os.path.exists(backup_path):
    os.makedirs(backup_path, exist_ok=True)

compress_type_map = {
    '.tar.gz': ['tar', '-czf'],
    '.zip': ['zip', '-r'],
    '.tar': ['tar', '-cf']
}

size_unit = ['B', 'KB', 'MB', 'GB', 'TB']
def get_folder_size(path: str) -> int:
    s = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            s += os.path.getsize(os.path.join(root, f))
    return s

def get_path_size(path: str) -> str:
    if os.path.isfile(path):
        size = os.path.getsize(path)
    else:
        size = get_folder_size(path)
    for unit in size_unit:
        if size < 1024:
            return f'{size:.2f}{unit}'
        size /= 1024
    return f'{size:.2f}{size_unit[-1]}'
     

def compress_directory(source: str, compress_type: str, output: str = None) -> str:
    if not os.path.exists(source):
        logger.error(f'{source} not exists', extra={'local': locals()})
        return None
    if compress_type not in accept_compress_type:
        logger.error(f'{compress_type} is not supported', extra={'local': locals()})
        return None
    
    date_str = date2str()
    if not os.path.exists(f'{temp_path}/{date_str}'):
        os.makedirs(f'{temp_path}/{date_str}')

    output_file_name = source[1:].replace('/', '_')
    try:
        if not output:
            output = f'{temp_path}/{date_str}/{output_file_name}{compress_type}'
        else:
            os.stat(os.path.dirname(output))
    except FileNotFoundError:
        return 'output path not exists'
    except Exception as e:
        logger.error(f'{e}', extra={'local': locals()})
        return None
    
    parent_path = os.path.dirname(source)

    if compress_type == '.zip' and not os.path.isdir(source):
        shell_command.pop()
    else:
        shell_command = [*compress_type_map[compress_type]]
    shell_command = [*shell_command, output, os.path.basename(source)]
    ret = subprocess.run(shell_command, capture_output=True, cwd=parent_path)
    if ret.returncode != 0:
        logger.error(
            f'backup {source} failed {shell_command}',
            extra={'local': locals(), 'output': ret.stdout.decode('utf-8'), 'error': ret.stderr.decode('utf-8')})
        return 'error, look log for more detail'

    return output

def main() -> Annotated[str, 'backup directory']:
    '''
    检索配置文件定义, 并打包(压缩)然后上传至阿里云盘
    '''
    with open('./config/backup.yml', 'r') as f:
        config = yaml.safe_load(f)
    keys = ['directory', 'mysql']
    assert set(config.keys()) == set(keys), f'config keys must be {keys}, but got {config.keys()}'

    def record_log(label: str, compress_type: str, dir: str, output: str):
        file_type = 'file' if os.path.isfile(dir) else 'directory'
        insert(
            'backup_log',
            (label, iso2str(), dir, compress_type, output, 'completed', file_type, get_path_size(dir), get_path_size(output)),
            backup_log_fields[1:]
        )

    date_str = date2str()
    if not os.path.exists(f'{temp_path}/{date_str}'):
        os.makedirs(f'{temp_path}/{date_str}', exist_ok=True)
    if not os.path.exists(f'{backup_path}/{date_str}'):
        os.makedirs(f'{backup_path}/{date_str}', exist_ok=True)

    for dir, c in config['directory'].items():
        output = f'{backup_path}/{date_str}/{dir[1:].replace('/', '_')}{c["compress_type"]}'
        ret = compress_directory(dir, c['compress_type'], output)
        if ret:
            record_log(dir, c['compress_type'], dir, output)
    
    for label, c in config['mysql'].items():
        label = 'mysql' + '#' + c['database'][0] + '#' + label + '#' + c['type']
        if c['type'] == 'docker':
            # TODO: 支持多个数据库
            cmd = ['docker', 'exec', c['container'], 'mysqldump', '-u', c['user'], f"-p'{c['password']}'", c['database'][0]]
            output = f'{temp_path}/{date_str}/{label}.sql'
            ret = subprocess.run(' '.join(cmd), shell=True, stdout=open(output, 'w'), cwd=temp_path, text=True)
            if ret.returncode != 0:
                logger.error(f'{cmd} failed', extra={'local': locals(), 'output': ret.stdout.decode('utf-8'), 'error': ret.stderr.decode('utf-8')})
                continue
        else:
            pass
        # compress
        compress_output = f'{backup_path}/{date_str}/{label}{c["compress_type"]}'
        ret = compress_directory(output, c['compress_type'], compress_output)
        if ret:
            record_log(label, c['compress_type'], output, ret)
        
    return f'{backup_path}/{date_str}'


if __name__ == '__main__':
    main()