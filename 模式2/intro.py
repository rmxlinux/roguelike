import roguelike_lib as rl
import json


path = "zh_CN/gamedata/excel/roguelike_topic_table.json"
with open(path, mode='r', encoding='utf-8', errors='ignore') as f:
    js = json.load(f)

name = rl.makediff()
if name == 'null':
    print('新肉鸽暂未找到，请手动查找或更新zh_CN')
    exit(0)

#name = 'rogue_4'

print(f'新肉鸽已经找到，name={name}')

end_items = rl.make_new_items(js, name)
rl.make_new_scenes(end_items, js, name)
rl.make_new_enemies()
rl.make_new_endings(js, name)