import os
import shutil
from UnityPy import AssetsManager
from pathlib import Path
import json

def check(json):
    result = {}
    flag = 0
    if len(json) == 1:
        if isinstance(json[next(iter(json))], list):
            l = json[next(iter(json))][0]
            if 'key' in l:
                flag = 1
                for ls in json[next(iter(json))]:
                    result[ls['key']] = ls['value']
                return result
    for key in json:
        if isinstance(json[key], list):
            if json[key]:
                l = json[key][0]
                if 'key' in l:
                    flag = 1
                    result[key] = {}
                    for ls in json[key]:
                        result[key][ls['key']] = ls['value']
                else:
                    result[key] = json[key]
    if not flag:
        result = json
    return result

def makejson(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        raw_json = json.load(f)
    result = check(raw_json)
    with open(path, 'w', encoding='utf-8', errors='ignore') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

def makestory(libs):
    if os.path.exists('zh_CN'):
        shutil.rmtree('zh_CN')
    os.makedirs('zh_CN/gamedata')

    am = AssetsManager()
    for file in os.listdir('Android/anon'):
        am.load_file('Android/anon/' + file)

    for asset in am.assets:
        for id, obj in asset.objects.items():
            if obj.type.name == 'TextAsset':
                if obj.container:
                    data = obj.read()
                    #print(data.m_Name,obj.byte_size, len())
                    path = obj.container.replace('dyn/', 'zh_CN/')
                    if not os.path.exists(os.path.dirname(path)):
                        os.makedirs(os.path.dirname(path))
                    if path.find('.txt') != -1 or path.find('.json') != -1:
                        with open(path, 'w', encoding='utf-8') as f:
                            print(data.m_Script, file=f, end='')

                    else:
                        with open(path, 'wb') as f:
                            f.write(data.m_Script.encode('utf-8', errors="surrogateescape"))

    for root, dir, files in os.walk('zh_CN/gamedata'):
        for file in files:
            for c in libs:
                if file.find(c) != -1:
                    path = root.replace('\\', '/') + '/' + file
                    with open(path, 'rb') as f, open('tmp.bytes', 'wb') as fb:
                        cnull = f.read(128).count(b'\x00')
                        print(path, cnull)
                        f.seek(128)
                        fb.write(f.read())
                    try:
                        command = f'flatc --raw-binary --defaults-json --strict-json --force-defaults --natural-utf8 -t -o ./{os.path.dirname(path)}/ FBS/{c}.fbs -- tmp.bytes'
                        #print(command)
                        os.system(command)
                        makejson(f'{os.path.dirname(path)}/tmp.json')
                        os.rename(f'{os.path.dirname(path)}/tmp.json', f'{os.path.dirname(path)}/{c}.json')
                    except Exception as e:
                        print(e)
                        print(file, c)
                    break



#makestory(['character_table'])
