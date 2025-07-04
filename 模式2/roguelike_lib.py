import json
import re

def makediff():
    path1 = "zh_CN/gamedata/excel/roguelike_topic_table.json"
    path2 = "roguelike_old.json"
    with open(path1, mode='r', encoding='utf-8', errors='ignore') as f:
        json1 = json.load(f)
    with open(path2, mode='r', encoding='utf-8', errors='ignore') as f:
        json2 = json.load(f)
    for key in json1["topics"]:
        if key not in json2["topics"]:
            return key

    return "null"

def make_new_items(js, name):
    end_items = []
    with open('items.txt', mode='w', encoding='utf-8', errors='ignore') as f:
        old_items = []
        for n in js["details"]:
            if n.strip() == name.strip():
                continue
            for item_key in js["details"][n]["items"]:
                item = js["details"][n]["items"][item_key]
                if item['name'].strip() not in old_items:
                    old_items.append(item['name'].strip())

        dup_items = []
        items = js["details"][name]["items"]
        print('*****结局藏品（可能不全）\n', file=f)
        for item_key in items:
            item = items[item_key]
            if item['usage'].find('让探索开启不同的方向') == -1:
                continue
            if item['usage'].find('机制物品') != -1:
                continue
            if item['name'].strip() in old_items:
                if item['name'].strip() not in dup_items:
                    dup_items.append(item['name'].strip())
                continue
            end_items.append(item['name'].strip())
            print('=' * 30, file=f)
            print(item['name']+'\n', file=f)
            print(item['usage'], file=f)

        print('=' * 30, file=f)
        print('\n*****普通藏品、分队及物品\n', file=f)
        for item_key in items:
            item = items[item_key]
            if item['usage'].find('让探索开启不同的方向') != -1:
                continue
            if item['usage'].find('机制物品') != -1:
                continue
            if item['name'].strip() in old_items:
                if item['name'].strip() not in dup_items:
                    dup_items.append(item['name'].strip())
                continue
            print('=' * 30, file=f)
            print(item['name']+'\n', file=f)
            print(item['usage'], file=f)

        print('=' * 30, file=f)
        print('包含之前肉鸽藏品：' + '、'.join(dup_items) + '\n', file=f)

    return end_items

def deal(ans):
    pattern = r'<[^>]*[$@/][^>]*>'
    if not ans:
        return ''
    ans = re.sub(pattern, '', ans)
    return ans

def make_new_scenes(end_items, js, name):
    with open('scenes.txt', mode='w', encoding='utf-8', errors='ignore') as f:
        choices = js["details"][name]["choices"]
        scenes = js["details"][name]["choiceScenes"]

        cache = []
        tmp = ''
        for scene_key in scenes:
            scene = scenes[scene_key]
            if scene_key.find('enter') != -1:
                if tmp:
                    cache.append(tmp)
                tmp = ''
                tmp += '=' * 30 + '\n'
                tmp += scene['title']+'\n\n'
                tmp += scene['description']+'\n\n'
            else:
                id = scene_key.split('_')[-1]

                for choice_key in choices:
                    choice = choices[choice_key]
                    if not choice['nextSceneId']:
                        continue
                    if choice['nextSceneId'].strip() == scene_key.strip():
                        tmp += f"===选择{id}：{choice['title']}          {deal(choice['description'])}\n"
                        break

        print('*****结局事件（可能不全）\n', file=f)

        for s in cache:
            for item in end_items:
                if s.find(item) != -1:
                    print(s, file=f)
                    break
        print('=' * 30, file=f)
        print('*****普通事件\n', file=f)

        for s in cache:
            flag = False
            for item in end_items:
                if s.find(item) != -1:
                    flag = True
                    break
            if not flag:
                print(s, file=f)



dict_attr = {
    "maxHp": "最大生命值",
    "atk": "攻击力",
    "def": "防御力",
    "magicResistance": "法术抗性",
    "moveSpeed": "移动速度",
    "lifePointReduce": "目标价值",
    "baseAttackTime": "攻击间隔",
    "hpRecoveryPerSec": "生命恢复速度",
    "spRecoveryPerSec": "技力恢复速度",
    "massLevel": "重量等级",
    "tauntLevel": "嘲讽等级",
    "stunImmune": "晕眩抗性",
    "silenceImmune": "沉默抗性",
    "sleepImmune": "沉睡抗性",
    "frozenImmune": "冻结抗性",
    "levitateImmune": "浮空抗性",
    "disarmedCombatImmune": "缴械抗性",
    "fearedImmune": "恐惧抗性",
    "attractImmune": "吸引抗性",
    "rangeRadius": "攻击范围半径"

}

def check(v):
    if v:
        return '有'
    else:
        return '无'

def print_enemy(f,en,enemy_data):
    en_name = en["Key"]
    enemy_info = en["Value"][0]["enemyData"]
    print('=' * 30, file=f)
    if enemy_info["name"]["m_value"]:
        print(enemy_info["name"]["m_value"] + '\n', file=f)
    if enemy_info["description"]["m_value"]:
        print(deal(enemy_info["description"]["m_value"]) + '\n', file=f)

    if en_name in enemy_data:
        for ability in enemy_data[en_name]["abilityList"]:
            print(deal(ability["text"]), file=f)

    print('\n===详细数据===', file=f)

    for level in en["Value"]:
        if len(en["Value"]) > 1:
            print(f'第{level["level"] + 1}阶段', file=f)
        enemy_info = level["enemyData"]
        cnt = 0
        for attr in enemy_info["attributes"]:
            if attr in dict_attr:
                if enemy_info["attributes"][attr]['m_defined'] == True or dict_attr[attr].find('抗性') != -1:
                    print(dict_attr[attr], end=' ', file=f)
                    if type(enemy_info["attributes"][attr]['m_value']) == bool:
                        print(check(enemy_info["attributes"][attr]['m_value']), end='   ', file=f)
                    else:
                        print(enemy_info["attributes"][attr]['m_value'], end='   ', file=f)
                    cnt += 1
                    if cnt == 7:
                        cnt = 0
                        print('', file=f)
        if cnt:
            print('', file=f)
        cnt = 0

        if not enemy_info["talentBlackboard"] and not enemy_info["skills"]:
            continue
        print('\n**其他技能及天赋数据（请根据数据名称及技能描述自行对照）：', file=f)
        if enemy_info["talentBlackboard"]:
            print('*天赋：', file=f)
            for t in enemy_info["talentBlackboard"]:
                print(f'{t["key"]} {t["value"]}   ', file=f)
        if enemy_info["skills"]:
            for s in enemy_info["skills"]:
                print(f'*技能{s["prefabKey"]}：', file=f)
                if not s["blackboard"]:
                    continue
                for t in s["blackboard"]:
                    print(f'{t["key"]} {t["value"]}   ', file=f)
def make_new_enemies():
    with open('enemies.txt', mode='w', encoding='utf-8', errors='ignore') as f:
        with open(f'zh_CN/gamedata/excel/enemy_handbook_table.json', mode='r', encoding='utf-8', errors='ignore') as rf:
            enemy_data = json.load(rf)["enemyData"]
        with open(f'zh_CN/gamedata/levels/enemydata/enemy_database.json', mode='r', encoding='utf-8', errors='ignore') as rf:
            enemy_base = json.load(rf)["enemies"]
        with open(f'enemy_database_old.json', mode='r', encoding='utf-8', errors='ignore') as rf:
            enemy_base_old = json.load(rf)["enemies"]

        enemy_data_old = []
        for en in enemy_base_old:
            enemy_data_old.append(en['Key'])

        print('精英敌人数据' + '\n', file=f)
        for en in enemy_base:
            en_name = en["Key"]
            if en_name in enemy_data_old:
                continue

            enemy_info = en["Value"][0]["enemyData"]
            if enemy_info["levelType"]["m_value"].strip() != "BOSS":
                continue
            print_enemy(f, en, enemy_data)

        print('\n普通敌人数据' + '\n', file=f)
        for en in enemy_base:
            en_name = en["Key"]
            if en_name in enemy_data_old:
                continue

            enemy_info = en["Value"][0]["enemyData"]
            if enemy_info["levelType"]["m_value"].strip() == "BOSS":
                continue
            print_enemy(f, en, enemy_data)

def make_new_endings(js, n):
    with open('endings.txt', mode='w', encoding='utf-8', errors='ignore') as f:
        endings = js["details"][n]["endings"]
        cnt = 0
        for ending_key in endings:
            ending = endings[ending_key]
            cnt += 1
            print('=' * 30, file=f)
            print(f"第{cnt}结局 {ending['name']}\n", file=f)
            if ending['desc']:
                print(ending['desc'], file=f)
            if ending['changeEndingDesc']:
                print(ending['changeEndingDesc'], file=f)

    with open('ending_stories.txt', mode='w', encoding='utf-8', errors='ignore') as f:
        cnt = 0
        for ending_key in endings:
            ending = endings[ending_key]
            st = {}
            for p in js["details"][n]["archiveComp"]["endbook"]["endbook"]:
                if js["details"][n]["archiveComp"]["endbook"]["endbook"][p]['endingId'].strip() == ending_key:
                    st = js["details"][n]["archiveComp"]["endbook"]["endbook"][p]
                    break
            cnt += 1
            print('=' * 30, file=f)
            print(f"第{cnt}结局 {ending['name']} 剧情\n", file=f)
            if "avgId" in st:
                path = 'zh_CN/gamedata/story/' + st['avgId'].lower() + '.txt'
            else:
                continue
            with open(path, 'r', encoding='utf-8', errors='ignore') as fr:
                flag = 0
                lines = fr.readlines()
                for line in lines:
                    if line.find('[name=') != -1:
                        st = line.find('[name="') + 7
                        ed = line.find('"', st)
                        name = line[st:ed]
                        flag = 1
                        f_line = name + ": " + line[line.find(']') + 1:].strip()
                        print(f_line, file=f)
                    if line.find(r'[Sticker(id="st1", multi = true, text="') != -1:
                        st = line.find(r'[Sticker(id="st1", multi = true, text="') + len(r'[Sticker(id="st1", multi = true, text="')
                        ed = line.find('"', st)
                        name = line[st:ed]
                        flag = 1
                        f_line = name
                        print(f_line.replace(r'\n', ''), file=f)
                    if line.strip()[0] != '[':
                        print(line.strip(), file=f)
            print('\n', file=f)

