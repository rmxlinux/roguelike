import requests
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from tqdm import tqdm
import time
import zipfile
import os
import shutil
from pathlib import Path
import msvcrt
import roguelike_lib as rl
import json


def check_apk_update(url):
    response = requests.head(url, allow_redirects=True)
    response.raise_for_status()
    last_modified = response.headers.get('Date')
    parsed_time = parsedate_to_datetime(last_modified)
    utc_time = parsed_time.replace(tzinfo=timezone.utc)
    unix_timestamp = int(utc_time.timestamp())
    current_utc = datetime.now(timezone.utc)
    time_diff = (current_utc - utc_time).total_seconds()
    recent_status = 1 if abs(time_diff) <= 7200 else 0
    return {
        'timestamp': unix_timestamp,
        'recent': recent_status
    }

def format_time(ts):
    current_time = datetime.fromtimestamp(ts)
    year = str(current_time.year).lstrip('0')
    month = str(current_time.month).lstrip('0')
    day = str(current_time.day).lstrip('0')
    hour = str(current_time.hour).lstrip('0')
    minute = str(current_time.minute)
    if current_time.minute < 10:
        minute = '0' + minute
    second = str(current_time.second)
    if current_time.second < 10:
        second = '0' + second
    formatted_time = "{}年{}月{}日 {}:{}:{}".format(year, month, day, hour, minute, second)
    return formatted_time


def download(url, save_path='tmp_apk.apk', chunk_size=8192):
    with requests.get(url, stream=True, timeout=30) as response:
        response.raise_for_status()
        total_size = int(response.headers.get('Content-Length', 0))
        progress = tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            desc=f"下载中...",
            ncols=80
        )
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    progress.update(len(chunk))
        progress.close()

def dozip(path):

    with zipfile.ZipFile('tmp_apk.apk', 'r') as f:
        progress = tqdm(
            total=len(f.infolist()),
            unit='file',
            unit_scale=True,
            desc=f"解压缩...",
            ncols=80
        )
        for file in f.infolist():
            file_path = file.filename.replace('\\', '/')
            if file_path.startswith(path):
                relative_path = os.path.relpath(file_path, path)
                dest_path = Path('Android/' + relative_path)
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with f.open(file_path) as source, open(dest_path, 'wb') as target:
                    target.write(source.read())
            progress.update(1)
        progress.close()

'''
print('正在检索安装包更新...')

resp = check_apk_update('https://ak.hypergryph.com/downloads/android_lastest')
while not resp['recent']:
    print(f'安装包未更新，最近更新时间 UTC {format_time(resp["timestamp"])}, 当前时间 {format_time(datetime.now(timezone.utc).timestamp())}')
    time.sleep(2)
    resp = check_apk_update('https://ak.hypergryph.com/downloads/android_lastest')

time1 = datetime.now().timestamp()

print('检测到安装包更新，开始下载...')

hurl = requests.head('https://ak.hypergryph.com/downloads/android_lastest').headers['location']
download(hurl)
print('下载完成，开始解压...')

if os.path.exists('Android'):
    shutil.rmtree('Android')
os.makedirs('Android')

dozip('assets/AB/Android/')

print('解压完成，请打开模拟器启动明日方舟')
print('热更新数据完成后，按任意键继续')
msvcrt.getch()

os.system('adb root')
os.system('adb pull /storage/emulated/0/Android/data/com.hypergryph.arknights/files/Bundles/anon')


print('暂不支持自动移动，请将文件夹内容手动移动到Android')
p4 = input()

if os.path.exists('Android_u'):
    shutil.rmtree('Android_u')
os.makedirs('Android_u')
os.makedirs('Android_u/anon')
os.system('python decompress.py Android/anon Android_u/anon')

shutil.rmtree('Android')
os.rename('Android_u', 'Android')

print('游戏数据下载完成，尝试解析...')

import makedata

need_libs = [
    'roguelike_topic_table',
    'enemy_handbook_table',
    'enemy_database'
]
makedata.makestory(need_libs)
'''
path = "zh_CN/gamedata/excel/roguelike_topic_table.json"
with open(path, mode='r', encoding='utf-8', errors='ignore') as f:
    js = json.load(f)
'''
name = rl.makediff()
if name == 'null':
    print('新肉鸽暂未找到，请手动查找或更新zh_CN')
    exit(0)
'''
name = 'rogue_4'
print(f'新肉鸽已经找到，name={name}')

end_items = rl.make_new_items(js, name)
rl.make_new_scenes(end_items, js, name)
rl.make_new_enemies()
rl.make_new_endings(js, name)
