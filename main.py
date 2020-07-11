# -*- coding: utf-8 -*-
# import tkinter as tk

import os
import re
import copy
import ssl
import json
import time
import base64
import urllib3
import win32con
import pyperclip
import random
import base64
import hashlib
from urllib.parse import urlencode
from urllib.parse import unquote as urldecode
from playsound import playsound
from system_hotkey import SystemHotkey

# 切换模式
def changemode(x):
    global MODE
    if (MODE == 0):
        MODE = 1
        if (os.path.exists('./1.mp3')):
            playsound('./1.mp3')
        print("-> 切换模式：剪贴板模式")
    elif MODE == 1:
        MODE = 2
        if (os.path.exists('./2.mp3')):
            playsound('./2.mp3')
        print("-> 切换模式：翻译模式： EN -> CN")
    elif MODE == 2:
        MODE = 3
        if (os.path.exists('./3.mp3')):
            playsound('./3.mp3')
        print("-> 切换模式：翻译模式： CN -> EN")
    else:
        MODE = 0
        if (os.path.exists('./0.mp3')):
            playsound('./0.mp3')
        print("-> 切换模式：搜索模式")

# 通用配置解析器
def comm_parse(arr):
    f = []
    for a in arr:
        if (a == ''):
            continue
        elif (a[0:1] == '#'):
            continue
        f.append(a)
    return f

# 选择节点
def select_node():
    global QCS
    global TSLTAPI_APPID
    global TSLTAPI_KEY
    global NOTE
    global NOTE_NODE
    print("=================================================")
    print("|| Select Central Node                         ||")
    print("|| 0: Github                                   ||")
    print("|| 1: Vercel                                   ||")
    print("=================================================")
    node = -1
    while (node not in [0, 1]):
        if (node != -1):
            print("!! 错误的中心节点编号")
        node = input("-> 选择中心节点编号(1)：")
        if (node == ''):
            node = 1 # 默认节点
        else:
            node = int(node)
    if node == 0 :
        QCS = NODE_GITHUB
    elif node == 1:
        QCS = NODE_VERCEL
    # 读取分支节点数据
    _nodes = HTTP.request('GET', QCS + "server_list.json")
    if (_nodes.status != 200):
        print("!! 读取服务器数据失败（code:1）")
        exit()
    _nodes = json.loads(_nodes.data.decode('UTF-8'))
    print("=================================================")
    print("|| Select Node")
    count = 0
    nodes = []
    for node in _nodes:
        print("|| " + str(count) + ": " + node['name'])
        nodes.append(count)
        count += 1
    print("=================================================")
    node_num = -1
    while (node_num not in nodes):
        if (node_num != -1):
            print("!! 错误的节点编号")
        node_num = int(input("-> 选择节点编号："))
    QCS = _nodes[node_num]['server']
    # 读取分支节点设置（百度翻译）
    print('-> 读取节点设置')
    _config = HTTP.request('GET', QCS + "config.json")
    if (_config.status != 200):
        print("!! 读取节点数据失败（code:2）")
        exit()
    _config = json.loads(_config.data.decode('UTF-8'))
    TSLTAPI_APPID = _config['TSLTAPI_APPID'] if 'TSLTAPI_APPID' in _config else ''
    TSLTAPI_KEY = _config['TSLTAPI_KEY'] if 'TSLTAPI_KEY' in _config else ''
    NOTE = _config['NOTE_LINK'] if 'NOTE_LINK' in _config else ''
    NOTE_NODE = _config['NOTE_NODE'] if 'NOTE_NODE' in _config else ''


# 选择模式
def select_mode():
    global MODE
    print("=================================================")
    print("|| Select MODE                                 ||")
    print("|| 0: Search                                   ||")
    print("|| 1: Clipboard                                ||")
    print("|| 2: Clipboard + Translate                    ||")
    print("|| 3: Clipboard + Translate                    ||")
    print("=================================================")
    while (MODE not in [0, 1, 2, 3]):
        if (MODE != -1):
            print("!! 错误的模式编号")
        MODE = int(input("-> 选择模式编号："))

# 获取白名单
def get_whitelist():
    global WHITELIST
    _whitelist = HTTP.request('GET', QCS + "whitelist.txt")
    if (_whitelist.status != 200):
        print("!! 读取服务器数据失败（code:1）")
        exit()
    _whitelist = _whitelist.data.decode().split("\n")
    WHITELIST = comm_parse(_whitelist)

# 登录
def login():
    auth = input("-> 请输入您的授权码：")
    if auth not in WHITELIST:
        print("!! 无效的授权码")
        time.sleep(3)
        login()

# 获取数据库列表
def get_databaselist():
    global DATABASELIST
    print("-> 正在拉取数据库列表")
    _databaselist = HTTP.request('GET', QCS + "lists.txt")
    if (_databaselist.status != 200):
        print("!! 拉取数据库列表失败（code:2）")
        input()
        exit()
    _databaselist = _databaselist.data.decode().split("\n")
    DATABASELIST = comm_parse(_databaselist)

# 选择数据库
def select_database():
    global DATABASELIST
    print("=================================================")
    print("|| Select Database")
    # print("|| #: Database Name")
    database_file = {}
    count = 0
    for database in DATABASELIST:
        d = database.split(',')
        database_file[count] = d
        # print(d[2])
        if (d[2] == '0'):
            continue
        elif (d[2] == '2'):
            dn = d[0] + " [MAINTAINING]"
            print("|| " + str(count) + ": " + dn)
        else:
            dn = d[0]
            print("|| " + str(count) + ": " + dn)
        count += 1
    print("=================================================")
    database_num = -1
    while (database_num not in database_file):
        if (database_num != -1):
            print("!! 错误的数据库编号")
        database_num = int(input("-> 选择数据库编号："))
    return database_file[database_num][1]

# 切割中英文
def slicer(txt):
    # 英语单词提取
    pattern_en = re.compile('[^a-zA-Z]*([a-zA-Z]+)[^a-zA-Z]*')
    # 中文提取
    pattern_zh = re.compile("[\u4e00-\u9fa5]")
    en = [item.lower() for item in re.findall(pattern_en, txt)]
    zh = re.findall(pattern_zh, txt)
    kw = en + zh
    return kw

def send_note(x):
    print('-> sending')
    if (os.path.exists('./0.mp3')):
        playsound('./0.mp3')
    cb = pyperclip.paste()
    if (cb == ''):
        if (os.path.exists('./0.mp3')):
            playsound('./0.mp3')
        print('-> 获取剪贴板内容失败')
        return False
    data = {
        'text': cb
    }
    print(data)
    send = HTTP.request('POST', NOTE + NOTE_NODE, fields=data)
    if (send.status == 200) :
        if (os.path.exists('./1.mp3')):
            playsound('./1.mp3')
    else:
        if (os.path.exists('./0.mp3')):
            playsound('./0.mp3')
    print('-> sent')

def receive_note(x):
    global CONTENT
    print('-> receiving')
    if (os.path.exists('./0.mp3')):
        playsound('./0.mp3')
    send = HTTP.request('GET', NOTE + '_tmp/' + NOTE_NODE)
    if (send.status == 200) :
        d = send.data.decode()
        pyperclip.copy(d)
        CONTENT = d
        if (os.path.exists('./1.mp3')):
            playsound('./1.mp3')
    else:
        if (os.path.exists('./0.mp3')):
            playsound('./0.mp3')
    print('-> received')

# 获取数据库
def get_database(database):
    global DATABASE
    print("-> 正在下载数据库：" + database)
    _database = HTTP.request('GET', QCS + "/databases/" + database + ".qcsd")
    if (_database.status != 200):
        print("!! 拉取数据库列表失败（code:2），回车退出")
        input()
        exit()
    _database = _database.data.decode().split('\n')
    database = []
    for d in _database:
        if d != '' and d[0:1] != '#':
            database.append(d)
    # print(database)
    print("-> 正在解析数据库")
    _database = {}
    count = 0
    while (len(database) != 0):
        DATABASE[count] = {}
        d = database.pop(0)
        if (d[0:2] == '->'):
            c = re.match("->[\s]*([\s\S]+)", d)
            if c :
                _database['question'] = c.group(1)
                keywords = slicer(c.group(1))
                _database['keywords'] = keywords
        elif(d[0:2] == '=>'):
            c = re.match("=>[\s]*([\s\S]+)", d)
            if c:
                _database['answer'] = c.group(1)
            DATABASE[count] = copy.deepcopy(_database);
            count += 1
    print("-> 数据库解析完成")

# 查找答案
def search(txt):
    global DATABASE
    print ("-> search: " + txt)
    if txt == '' :
        return False
    txt_arr = slicer(txt)
    # 仅含无法解析与搜索的特殊字符
    if len(txt_arr) == 0:
        if (os.path.exists('./0.mp3')):
            playsound('./0.mp3')
        print("-> 查找失败：无法解析的内容")
        return False
    # 加权搜索
    right = {}
    _copy_DATABASE = copy.deepcopy(DATABASE)
    for count in _copy_DATABASE:
        # 权重初始化
        right[count] = 0
        # 匹配计数
        match = 0
        # 初始化查找值
        _find = copy.deepcopy(txt_arr)
        for f in _find:
            if f in _copy_DATABASE[count]['keywords']:
                # 成功找到关键字
                _copy_DATABASE[count]['keywords'].remove(f)
                right[count] += 1
                match += 1
            else:
                # 无关键字
                right[count] -= 1
        if match == 0:
            # 无匹配删除
            right.pop(count)
        else:
            # 剩余结算
            right[count] -= len(_copy_DATABASE[count]['keywords'])
    # print(right)
    if (len(right) == 0):
        if (os.path.exists('./0.mp3')):
            playsound('./0.mp3')
        print("-> 未找到匹配内容")
        return False
    else:
        # 查找最大值
        key = 0
        max_right = -999
        for i in right:
            if (right[i] >= max_right):
                key = i
                max_right = right[i]
        qusetion = DATABASE[key]['question']
        answer = DATABASE[key]['answer']
        print("-> 成功查找到匹配值")
        if (os.path.exists('./1.mp3')):
            playsound('./1.mp3')
        print("=================================================")
        print("-> Q:" + qusetion)
        print("-> A:" + answer)
        print("=================================================")
        return answer

# 翻译
def translate(txt):
    print ("-> translate: " + txt)
    if MODE == 2:
        if (os.path.exists('./2.mp3')):
            playsound('./2.mp3')
    elif MODE == 3:
        if (os.path.exists('./3.mp3')):
            playsound('./3.mp3')
    salt = str(random.randint(1000000000,9999999999))
    md5 = hashlib.md5()
    s = TSLTAPI_APPID + txt + salt + TSLTAPI_KEY
    md5.update(s.encode(encoding='UTF-8'))
    sign = md5.hexdigest()
    if MODE == 2:
        t_from = 'en'
        t_to = 'zh'
    else:
        t_from = 'zh'
        t_to = 'en'
    data = {
        'q': txt,
        'from': t_from,
        'to': t_to,
        'appid': TSLTAPI_APPID,
        "salt": salt,
        'sign': sign
    }
    data = HTTP.request('GET', TSLTAPI + "?" + urlencode(data), headers = {"Content-Type": "application/x-www-form-urlencoded"})
    if (data):
        if (os.path.exists('./1.mp3')):
            playsound('./1.mp3')
        data = json.loads(data.data.decode('utf-8'))
        # 整合结果
        dist = ''
        for d in data['trans_result']:
            dist += d['dst'] + "\r\n"
        dist = urldecode(dist)[0:-2]
        print('-> 翻译结果：' + dist)
        return dist
    else:
        if (os.path.exists('./0.mp3')):
            playsound('./0.mp3')
        print('-> 翻译失败')
        return False

# 剪贴板监听
def clipboard_listen():
    global MODE
    global CONTENT
    CONTENT = pyperclip.paste()
    print("-> 开始监听剪贴板")
    while(True):
        clip = pyperclip.paste()
        if (CONTENT != clip):
            if (clip == ''):
                continue
            print("-> 正在查找...")
            # 处理
            if MODE == 0:
                res = search(clip)
                CONTENT = clip
            elif MODE == 1:
                res = search(clip)
                if (res):
                    print("-> 复制到剪贴板")
                    pyperclip.copy(res)
                    CONTENT = res
                else:
                    CONTENT = clip
            elif MODE == 2 or MODE == 3:
                # 翻译
                res = translate(clip)
                if (res):
                    print("-> 复制翻译结果到剪贴板")
                    pyperclip.copy(res)
                    CONTENT = res
                else:
                    CONTENT = clip
            time.sleep(2)

# 主程序
def main() :
    print("=================================================")
    print("||                 QUIC SEARCH                 ||")
    print("||                Author: Jokin                ||")
    print("||               Version: v1.3.1               ||")
    print("=================================================")
    # 写音效文件
    if (os.path.exists('./0.mp3') == False):
        print('wir')
        with open('./0.mp3', 'wb') as f:
            f.write(base64.b64decode(S0))
            f.close
    if (os.path.exists('./1.mp3') == False):
        with open('./1.mp3', 'wb') as f:
            f.write(base64.b64decode(S1))
            f.close
    if (os.path.exists('./2.mp3') == False):
        with open('./2.mp3', 'wb') as f:
            f.write(base64.b64decode(S2))
            f.close
    if (os.path.exists('./3.mp3') == False):
        with open('./3.mp3', 'wb') as f:
            f.write(base64.b64decode(S3))
            f.close
    # 中心节点选择 改快捷键操作
    select_node()
    print("-> 初始化中，请稍候...")
    # 注册热键 hotkey
    hk = SystemHotkey()
    hk.register(('control', 'shift', 'alt', 'z'), callback=changemode)
    hk.register(('control', 'shift', 'alt', 's'), callback=send_note)
    hk.register(('control', 'shift', 'alt', 'x'), callback=receive_note)
    # 获取白名单
    get_whitelist()
    print("-> 初始化完成！")
    # 授权
    login()
    # 模式选择 默认0模式
    # select_mode()
    # 获取数据库列表
    get_databaselist()
    # 选择数据库
    database = select_database()
    # print(database)
    # 获取数据库
    get_database(database)
    # 剪贴板监听
    clipboard_listen()

if __name__ == '__main__':
    # 剪贴板缓存
    global CONTENT
    # 基础获取地址
    global NODE
    global NODE_GITHUB
    global NODE_VERCEL
    NODE = ""
    NODE_GITHUB = "https://tools.990521.xyz/quicsearch_servers/"
    NODE_VERCEL = "https://tools2.990521.xyz/quicsearch_servers/"
    global QCS
    QCS = NODE_VERCEL
    # 百度翻译API
    global TSLTAPI
    global TSLTAPI_APPID
    global TSLTAPI_KEY
    TSLTAPI = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    TSLTAPI_APPID = "BAIDU_TRANSLATE_APPID"
    TSLTAPI_KEY = "BAIDU_TRANSLATE_KEY"
    # 关闭证书验证
    ssl._create_default_https_context = ssl._create_unverified_context
    # 取消关闭验证安全提醒
    urllib3.disable_warnings()
    # urllib3实例
    global HTTP
    HTTP = urllib3.PoolManager()
    # 模式： 0 搜索模式 1 剪贴板模式 2 英译中 3 中译英
    global MODE
    MODE = 0
    # 白名单
    global WHITELIST
    WHITELIST = ['joe']
    # 数据库列表
    global DATABASELIST
    # 数据库
    global DATABASE
    DATABASE = {}
    # 云便签
    global NOTE
    global NOTE_NODE
    NOTE = 'http://Your.Note.Link/'
    NOTE_NODE = 'supernote4qcs'
    # 音效
    global S0
    global S1
    global S2
    global S3
    S0 = "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2GSSo2dM7bcV3+P92d76l087z/v15jXbvP9P/H7urf/8/9+WfvX+LfG3P/93mL7F9XeHGOYBAYToJ5lPDOmDKBiJAboZGC2AeYMgQhjwmFGogOSYKICJgogsGCSBkYLQB5gWAHm5ELKmCInSne5imcHKkeeSMJGAW9ElR4EgDT3dZQhxkOM1VXWyB6oJS9f5sC1W6wibkDvNbiEpbWUPWp6o/azUbWDwHZtBQOLYcEHHESzzbP6ziSeX7/soDrKGFUfCrKkkdud0CdM27ZKUsrD7zuzeqqH+zEvmuTzmZH+jz0YZCpudv5nO/nINx3eTpe6b5j0v/J3MgpeYxmdsp3KrOQuIxwTjoAyMrhIwACAoBDAwNCgMMHE8xcPjGYwFhP/7ksQPghcBuRYOYM3KjjQhVbehucleAhDQARZCpFZPiPQJRQy8EGRRsDPXGh1Z67Frs1UzlsFYRJn2S7NzTmzUvvUMPu9AN2m1X3Yb2noHqhTZ5uVyIsnwsJGIQgUggoq7J6m7pkzDEOcYopDTyz188suKwhmSpWpWnbrf+Ij5jRuvb6W75ERjeIf2+7q9jGiGaW13u7fv4jPGQrby7+07YyLfIcf9Pez9xogCCoBgbV0nyOZl8gcq2GinBoaUaOfGgqhs68CiwxsSDgKFwQmM0sgE8TWPRma0NccsrWoecqwrlc/Q2NmDF0iidKItyhYXF82oarUNQ1XTtrKxR1a9Ts+m1DQWg1FQ9UoGwNg+FhYWFjiRUVFRU2G9g6OmGYpelFVlVa9ima/+VVVX+GbVfb//9mvX2//bv//2Zv9lVdVVf4b/ZVVVVVFbhHS8NJDaTEFNRTMuOTcgKGJldGEpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqr/+5LEKAPAAAGkAAAAIAAANIAAAASqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"
    S1 = "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qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqv/7ksSbA8AAAaQcAAAgAAA0gAAABKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqo="
    S2 = "SUQzBAAAAAAAF1RTU0UAAAANAAADTGF2ZjUyLjY0LjIA//uQZAAA8fwVSWgvQcAAAA0gAAABD+kPKYTlq4AAADSAAAAErSSAAAEBan8lgAVN/P+GDRuDHEcFIhkLzp+7u8C4KwXlB5hgvgg6UCL/y45xf//6Uf0WeU9Sf+D5+sPE+ku+gWyuAAAABXoB4SersSKVRqGm7WoemlHjFUNJE24TplKDmrRecjFfPdevlcmqWUyplTP1FF+NbhoJGXmQ6DKu7EiTiKXh5pkmfLh03VrXdJaqluYGi0zhpXpr/Ugm9ZgXDRb+zoqXoLZN1IIMZnwsEAlrHYgd+IFHAsEX/lAQOEFx22sBAEIpSdQ2ET/KhmTQZnJRaJwCZrj7agJYYwsT4uM0Nnlmcf2AIRYsaz7hlvXauEad5YYZEL0LshNup9+3/Of/MP5nzGYFjAGAk4SuOr0+5ZfPJcfdNQLNyuZm93ET5zoXbX1/WeBf+sLa5WY21Yxp9Kv53CHPb7+M/O1KrTSRR6n2nDoQyJnW7MjyXbWoDhZjrUrleHI3mmsSMDyJrF3zen19csiDV6hUhOCfmEW0hbTAeZp7yVfJBOQU//uSZF8A9jVnzemZe3YAAA0gAAABGImLKIZzDcAAADSAAAAEVZtiuTW7is6pruVYAng6UdHcrq1s8hxIOFiLz7+rGRcMFlo2DzjdBGDAa5b8wU2CelUE35qH4ajF/dPTR95namASGDIIXXBbbybiL9ZV6evMRylvSuj12NzVGwYVQbRq8jsxqYn7litcxs40lLby/PKPrlR0MJy9cn59SnuXr//q3cq59/VaXPClgBRl03m7jhft8y7v7lJUvyqMztzGOyynsc7nl+GVXf/n3//eq2XbNPT/jut9Pl3f71rDuNXG7zDlPb1+VOWaatvaKglY6AB+azWcOkA0okWAMZJyzapH6BoUMDRI8QKUa2xPpLlDJ59arN5HL4Ej1HYsx6W5UFNJBESQMoHdfm1UgSrjjboIzWosdzFukNTRiCBBojEnDM0URxwxNXTMTpmms2RWYJmBZBC4NhirpMidU2YoopZqXjFx9BakMCGJULqdNtNE1lgoF8ySN0kDxmdZm0j6aSLpVWW2yjpMH7McKikLUUmRQUt6jhiQQvrcyW699v/7kmRYgvWbY0og3JNwAAANIAAAARNxcTGE7a3AAAA0gAAABIs1Mdl/YAAn3DxS1PldIpLj9LfhOMBMJAQOCSc6c3NQAXOe2Ixl2otLLsoyjnN/vdWAH8urbJgMxQVDAWkytc5z9b1nrLe+ZVj47AdgHuAUI5k7LcvIl5D1HU1lxiTEIIKCuiYnv/XQQZlm5OHsTwW0YFkq3f2n0zA0TM1FApGqLvfZjG6Sepk6akjprV1Isz00ml8QExglMlSNqn8tDcrZAABcurKlFhdv84/E4bqRwACQECTQEY4dmMjIQcKtykcupaaV517V+zX5DEOwOt1IZN0wADDmfvI9I2df6+YzxtcnFWxLp0tqEn8tVtnD6NvGPX/2li0hVhSxcbrr//Os/4pbdf/Bi5i1rj2x///l69rChRrlg9RUBSrss/4VDQsDRX4lGhxpUqNFVUZGgJ8LdJVa7NBcIAQBiBphFB1+A/nGaxs0Rk0JkSAGeLWc1rsmJ8HEEiFyJkcKGrCiO1oa3UaDXW4c+LWzjG4LxyewNQQmCp2WFQVVWeOic6D/+5JkcAL0OEXK2Rt64AAADSAAAAEOSIMYpOnpQAAANIAAAASpJmbhwVM5Y1eqEb3CHcrrGezjRi//sdKa1RcEACKpZ4bkjzkWAU5bgvBa30cSlpmsYRaLVYgrqJtYRyLAoMpAkJoLGgYPEFqwlguA5zSpjdM3M3ZN1OpJab01unQZOuuizO71LTMC4XLkDjVvMgF8i4cwT2JMVPC7QmKJMli6Dnl/Tz5Dqu1NvZSswtqb0JK0UgfklisG5u+tPBzIZ/Bb6uzN5wHStig0KBhVDSsTMiTDcoo5RkNDBDJBQvCAgQw9UMWYwg/NHRQELmUDTSWSA4DFgAwEFMCBDBRsUGDEUw0oNNhNzQog35SMGIzR103NrM9BTI1EME2IMjYOut084Ga+1/KUTdNGKtq+/k5K3bctTNQdL9zGdySWy/fcPz/f4Z565h+dPG5fT3JmBIfuTcvzt7p7sbn8LtupY3SWMP/O5DFJUq2pZwE3/1g+J2P1h9ScH1Blb4YVP//BqUB/FI4WDQqDQJYTIp7DeqvMqKvBIUAJfQw+XDNZFOQ1//uSZLIA85Inxsn5alAAAA0gAAABGaEZLUZva5AAADSAAAAEQ74riIUMTMEAMtygBfN9HZYa4r/zUJt0vxu1KYdrMGkTEkJwEBIjDA0DX8fjjpO5NQJUlW4cjbpO7RXLUSlWLsuSymcEQUWIAJccBsZ4NFZdu1lYw5Xn6vP+tErk9TRq1ALGWSKjDgCEtg8D0UWm5TakcN1IxZuYTuuW601bgOabCxpaZeRYVp9/6m6+ffyvYWrmGufZ3QP7BEjjL1OiyexTyi992Ny/VL9Tfa9PfrZZ4ZXaS/RO/Hoci9ynLCJ1lv/2AAAAAbncQbtHOSCOM/Uy+kpxvyyVRSLscDh+YlBhIPBDNUBTEWXWW0l89d7LMN09W/nq79bGcy3d3GBGHGKyitcp73MM6Ji4XjO6Kp5IzZJzM4EfATiXDBJbUEjFaKXSrbqrLxwRobIFSaF4iSysjuhbMmQMTBM3MBZQe01KikqyjJBBabVKddqDmIropQfiCDkEqM8RhkgWSBE8XhekMIAmbqOIFA4iVhcI3RXwtcFgIMXkjQ2MEAlWKv/7kmTRAPccZMxJPNN6AAANIAAAARetnzGk8m3AAAA0gAAABEs+IGepszaTRNVhKIBHff2l3Wxh6hbgOgCDABIQUMKyVOpxEMSwAQsXFKXTryOBI/KbUsrU92W0t21KM6Knp7NdqgiBV5Y63t7XeUdjZSHQZGJoXzR0DY6Ti1nURTQRSxAo4xwlg11nDF0H1oHTKkpaaCJMixk4TQ1SAFYiJCEifN3OJpJK0HMlFgnzY6oL8C4S0dUgfTRuijWg2pnNkUbLFcEERwl5M4UyktOt0HWfT3UupFBEyGYQNjzR3850SSX5AFrFcsHDIIDAY1LI3qveiccf94CoNzDQ0NS585CcgEBVdKC07ixeDIphzVa1upylu2t85M37kcS8DgNT1aTf61SdmzIhqJfKqCKj5kbmhWLJKhl8AkoE0jmppLTTdzVBR59TKdVBZYOk2O8UVrm5cMyZTNDJNVd6nUdOOYEQIoSwgYqtrQXqTpUm9S3QLiBiMk1VlIOpS6l2vfRQQUak+Tp9r11VSlr1AAA7tu7BFp9oFVj2+Z1JaytdYqD/+5Jkv4P1/mRLIT2jcgAADSAAAAEU9Y0wgfJtwAAANIAAAAQzLrtM8x4yqvAxLiwFWtGn+aFS2IrrXa17Kjpr9yMRh3H4bGzJpaXzBrdXHD/y3rLsJXT1e5tAs5qc2C6nIISJiW1G3ri3t/jON//yxmx7ar9aL6PSZMW3rFtim823j/X/1PTFUUhyHM0OL8f4t//8fO/91k0+jWfPt//+0O1v943SHTOrZxvG7PtxooBUgC+dc+egfYjXry4HkNvg0Vn7BE6hUHMSDwCpHKwwzGnrYJk5Wa4PorJ0udAjhzkFwzBUXirxRt3WlPm4TlO9lx9o27s1Yta7/5U342f2aMBsPJFmDoBYLAIgRDo9maG/X5qGvrKHhyIrTBI2ma+GaVpmb2//WoWmZpr/Zv+Ka5i1WOf/+Lyjt3/9ShQHhC7S63uU0ZGuMEMEqJeCREEbc4BWHgd7FaU4xEE54YEnoDmmOmfUl8TrM5ZW55eRAYCg0Yy9iomGNbl1iet2sJBTY3afeFi/Vu5YU9rHLn7zxCkN5EQSCKrULESy6Fv4pTK6//uSZMqC9RlizFh8e3IAAA0gAAABEYljIQZtDcAAADSAAAAEGUuepEXCyy+Obr3aEmUvZrelJNiRyLMqhW+ZeKwJ36y6d569e/ewgFOReBKEQAULAAnu9VJxn8gKixF18DUFXRJwoGVuVqCgBCwGMGgEFCgBDsxcEjFZRMSC0ymJTDyANZOQ3U/jkE0OqSg385DBTHOoJw0irzDCCMZB8xSA25GBgEjO54NBaA5NRvUU2eSGfhDTIDUeLkJMgIDmAQOj0tRAWYHCphkMmEwSmwWABQdoYYfYZY9DId6XL4wu3I0F9zQxYT8ZkkZKsaHnOZaj3l+1IY4XhscY60wlEPtSIf62p3acbVG2OEOPe974eaeQTQWI8CazysdvZlAxwprTXw8ifP16P7+/gRM39IGoe8X3uBFfyZv76zfFKPJrw5/cgId2P//CqUBmg9ByJAfIYkiYUDK/a1ljVq09JZw7V1K3KWSWlGAADA7A8MGcHAWABMFwPMxDBWTDAGtMwpUYzuhsDBQBvMBADIMBbIAAUkUcmgpbPu2aUS6PztvfcP/7kmTxgPSLV0OrGRtyAAANIAAAAR7Nkxjn8e3IAAA0gAAABJZWm4Ysuzp1ICfBTZk0rR5QwQpUcM8E3OAGpLoPiuc5nnQ02GH7t54Y6syvP88I1D8tpeT0gYqkUOArydsEIAphq0+zSJWmSwFErMgyl+qSWYVY7L4dg9usatyWmvy2w/MBNfYox5xUPjSUAzDV78OXu/jlhhW7clGcrz3vPKzSwPb7h8nltiJPbI/zq9mIxupnS1MabuFTCooFJNWwAAEbP1BMaVQuJSwXg4V5z0utS+appqrIq9La5C5RC2ajwFGMYRFnS65ljXx6IRoCJhDuhIg93mIvjHJTKn0l1Nd7YzuV86K1bv4Sy7MT1JS4WMJdHUtjWFe+Y1vlfPCvqpe1rDm8d597+H1rf4avzEspY7FGtCK0DLtyft05dKpLGJ2xqrK6Sr3PmM5Lq8DxutWv8+1azz7dpBCICbzOCk2XM8b+VaGMKLnIheww5GJbEpA3B2YewgOSQJjUhGe9UMqbSnmpuM3LU5FKluZ1RV+F9Z6nCUt/ZGeee4zg7YD/+5Jk7ID3qWbLyZ7LegAADSAAAAEbHZ8rhPctyAAANIAAAARkugltPD1BY7K+Ve2LlakmZTG2ekwBg4UggFTAQKTBlNjj83xGBik3viEki1HN38eY3OZ47mM6O9hz92LOzE0J01WiWCdFpA2mIGQx1umk6JXUeRvoMlVWgmlqUiaqcviMAMmARSGURIuUGmKTGBjMFMmT6yqePEXSMDZCvPKZIuDlgPOFlJAG2OJKsyLLdJkDVi8gbmyPPUjs6tiYIOt1l46XTzAUP/55BRGV5hjCs29VLmCTQTASCGSz0ZmbM1YrWauWWPdzVLoRAEwaDw4DGDQoa+sh585AobpCQqAq8HZVtVsc+frf9/8Ob7zu80DVkDdNhzwI6IIksXlaKnWkzqZV/10EnqUtyqXxnwxEMcWySOy2ZEkkkdU61Jql0xNTqSJutNba1oTAVwPlGWJEzRXdpmmgjWt3SseYyWgqipBBEzRTMC8XnBV0RdGV//n7I2V0hnQAAADO9d30kCtioEfyL1b+ctlOVv9/hymxqNZBIOMBCYzmnz4d+Mfi//uSZMSD9aJjzCE9m3IAAA0gAAABFPWBNcRyTcgAADSAAAAEBFdgjt1bV+zfvT2G8u4b/nf/88+a1o8qmS5cDkAqQBCNzRTXRZSTavXq223US5fHGFTHKSpofW6KRuyLPRd7LsZKdFE0W1ZcLhcGENR7DyJY2SWntTRSr1IPqUikbNpIrZJZgmXVPFg6FmC1OgJpTVEcDJMfStBoLSA7lcbm7laUPowxrkpS/aemmzowACFRUBFRkwgZ2emfGRzbweaSHtZ5uAePAxaGVXJ+l+lrT17DH9/vu9Xu50mF2mf0RoYEFuBHQTwB0jCAtxaUVJ2ZnMpiqrpa+qxuUTYmibCeAnQJ0HOOs6mUti8js6TP0zWYqXJEmFpdJE2SMhhiWNltpOvdaL6looP1JMbI62rLpryREksypUxBTUUzLjk5LjVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVM0g9E3L8Jtvacpqr84TS5lAS8KpVS2BGAGHiBaMxonDBowYNBpgZaEmlFZlbkZ2CmUJpxSSctjm2ARl4UGDoOAmuv1LaG1Ko1f/7kmTVg/TSX01w3GtwAAANIAAAARTpdSqEba3AAAA0gAAABKq0WWWWrVcOhGFRCEAeJADPA0oQRDAiDUIUOdUoqVhuLWpX/rmChqHA1IR1Y7EFWg6drVpVHiLnl65WvYdEF38+2wsvyLwvblV87Qgfrvlo72nzgXtI84EY6U8q0KJKdUA6FKa8NVQLDMNWZ2ndKRZ2qOVtIsPCulKlmsQMUQEJBaczwyP2p2/KcM52rXqd5/z9WZs5U/cLuHb1vWH05SbARZEs7D5ZaGmMQvSTnG+B7xbMu5khmZZypTkFChhMpnpMt5PSmCN5jJHkGSRJQeYW0YQPpyTuUltx4P1ydJOZr2kURjSjcGwkQIcxiDA9pqJi0hNzpRprcqXYwQo6mAtg2CcE/G+EPAWwLghBeFBCiPG6AaZmXEllomh0EFWpygTAfAApALeQbnANhG2T5sT582UfUmaKQoLVpIsyLuk5ugbJuy0kJgidSZ1IKUeZOkeWo8uyClskpqC3orQKBeRUqyVa00UTBkWQVZ55VmY+ybmCbLdE2NKbu6VBFkj/+5Jk44/09UlEgZtC8gAADSAAAAEU2bEEB+TNyAAANIAAAATjLRQUyk2UYOiiya1GeipFTIopF4/x+i7CYswLAAgAAAcbrp2xQQQM7iItI8pyTYwDnat3BcVEZmLJCtzUfJCieiZIuGRwxGBEBoGAULYccCwAh8EWFngYAwBhsgFgEAYgwMgYnC+gcr+2gf0YlpOzMAUHADAiBMQMRc3A1/pfAxKimBgUAFARic6dnZa6C5PB05wg4yoYDZ1LWklN3QQVDC4GAoCQGBQBwWkANAAGYPIJOt0UnUt9JlLUVDM+T45YbeAMBQV0OXZSbUXTSVQTNzf11gYJQjgYTwSgOAABg9A6BYAZXHPLxBCYIA/X13U61VJrUgaXpqUpyCCdzI8CIAoGAkAojcMwDfw98gg/iCYgATl1of///3ZP///8uFdRpQI1NWhkAAAoDrG8FuLsTo8i5K73UyD0jUOJ+MKWtmZ2ra81NAEvrZZXbdV9XJhlhrvOEreXlMEg3MShLMShTMHvWNHWVMVxzDDeMBQECAKj3LU3Yv4dnp65KOzm//uSZP+ABOhjwoU+YAIAAA0goAABILYRFLmrAAAAADSDAAAAdy1YlkzUr6vfZ3csapuT9bJ0kxlrDASgwDrdC7F7d27Q2+/+tY///+7Xe/Uu9tVsKSI1ccc6sdfmGYo45h2DsQep9pf3Xd59wbPAUphtT1plcMuuhkzlCXG6V6occuJqvdqAVprzRLCAUpoenqVnJalACY3iGuSClutIn5bzstid/Crn+O5Lu/qrL5cGW5fk+ZK7PEMgkAAGfV4tgatk1Y2WFS7dy472UvmbeNjPGhv2Na5vmWX3pmN2UawwBTFt9jykiTA4UTEsEGCw0125Zvdy3Q3NVd6/nPrKNEDBbqTQWt2dZ5mRccIPQXDKndBBB+pf2q3dJEtmqMtpopTamoRUGuBkSwXSeKibGarnzVZgeZEmi+aEyRZN3L5Pk0ZlumbLHSiQNMymhOgaoF4omBDxzkEmUhQbrZIzTRUpRgszmzgkNGeImUQwBAzPHpyxCIyxMhAMANSQXohYppdbw5umqxqph9zLHXf1QQC4j/hwGGKoinuIiGEQjhUDl//7kmTtAPdpZMx/P6ACAAANIOAAARZdmTfE9m3AAAA0gAAABEwU8sou6725ax/HLD8M88Ezi1XrekkpC7oImYfwTaXED6aklfrdTV6upc8bqRUfoOkbLPMJsA/NGgV0TGikk62NjA6SjJpk0OUdLxZZ0kUiZNybJwnlEVIKUiwcTMzEdYGU5IF4jiZLSqkNuk7sZGgK7lSR4maqzRMOggAAAUfHwvXWnEgB0EgmHo5NXpbJrUbt501Xt7uHebv/2vhMwA0lLwVDsx9f877KARjWRBS6UOzOO7Pb/8tW8MOa7zdVztS1UkE3SfU5wzSC1ALKTdFNNbNfV+7LpqTZJNRigtFKximYxlAFoArIiRNIoHEjCzzcqEyXTdzxPj2XRchUWcL40iOIANwxKpiUR2kDFZIZUTogOAukAIw4zhBCbLTHhOQ0k3ExIDw7ITJMQU1FqqqqEkZ3mGIAAADPe1rOpygqfBEgrSuVUl2YgHeN3f467l9azE7TpzRbBKEweNTK6dN0wk5lujnoyBo7MgANVJpsWpble5jrust7x1/dasz/+5Jk3AD1e2LOcT2bcAAADSAAAAEWkXE35PZtwAAANIAAAAT+YIp0kE0zMcYc8AeAC2GCe1aKKKntq+q3pM5QOMZpmaZmF3FuE4BNCBBvFp5A2qY2qv/a/pKqTXoF8c58fxNgkojASIfS4Wnjya7eVMGxxvpE40hNSVAZ2+cp4dCUEBm4fhqnpow+9+KPvBkRcVhymKcxeUgAiY6OIVCDeGExMYbARjRDmxmqa0g55LbnMDyYJJRhAEGORQMglMx75y/yr361rDuv/v5bh61t205EmlRc5QlE4igAiABGX/q4c7/3f8Q7/dKlOaSQ8jpHaHkCEB8O8AEmGZ1yKyJqamrHT+62+7a6/5r+HSathUB6fWc42tpqxEYev4ifVywdTEFNRTMuOTkuNaqqqqqqqqqqqqqqqqqqqqqqqqqqAQAQAIxOLr9GtOC2DqlbDvJVD0lXbAbEWwQekTDELkCpoYcp3qCHkxkViQEHEmAqbR6uQCgYYwDWMuQVPOqlMJBOrTR2dcr8xVzYJY2SzalKKAMS9c47cEScFOw7zOvrxjz///uSZOWD9QJbTfE8a3AAAA0gAAABFTlrKoNxbcAAADSAAAAED/a+fvW9q77lMk8ya+f9kui7t/X/t23Pvvq7pN9aceUrwl2YGk+2HtoR8mVM9lbs7hxBzU4HVVS2SkRRMEMVWOSw+2R0YBCOWp0EANxQXbPCm4q7WgkgWrBQLLAAMEARAcsSA1ntIZbE3KgVBhwg4TJrL+DgwZCBRgcuHIwqIAWTAbKtGa9Fj2/bwt3/sZYU81lflibFoLlihcTvvGYxriskQsLrswmhl39Z00RVODi+RXUTRGYoLRJtwzDjcFFQeZqKx6BPJ740nSlrJRpvyiYkptalCJlDOczJxeZEQmenupLtF4LLqFD70Leaq0q5RdAtN8okqhdTFDxR1QIkQAFWkSyVMBEJ0yJDZMVncmBwj5rrtLZl0vZSxGis1Mu2Jjdyw/zc3Ipp2HU5gECPCKBQUt41h/KN36fCM6s7wsVMv/PnbOWX7pLe7/b+reH4a/n5ZY879rj0fucST9A6UucK8Iw6xbWOz/Fa2IEortgPTuPtVpeNfTFGuxN4sf/7kmTwifSzVEOxmTLyAAANIAAAARkxtQIM8S3AAAA0gAAABCE3fLGI4AAEgAAkpASrF/2Dp/mVJ3r/F40TjJSnNX+SVofMq8ffJWj7NNG5JWYA2ZscFLCxYwCARlasZgyMJjyEaggICQwFKE0+lZlrWMYHumYormBgWAUCF0qYns6xnS9Cmh4FrrBACT+v1/x6KRvWGhYDG6siksALo////y5LN97+nTbnDbQ5U7Kdf/zWG///z+fxh+GJzNelA7DAnVa+iE7EP/vn//cfx+BHgZIy+alljdvVIDgVFQSIgNMGgIQlJML/VIoI5Tufnruu/3fP7vD/syu3GIZafF88909u3hBy3bz3BUDAAF48K4cAQGAiMNbdNzn+Vv//3////////////////+t9////////////////kcYnWsIR126JgAwE1OQBdUIQEgSEEsDyUEM+E9bBKd36e3yvu3fhyvEtZc+XXJVLqB2mLr+Z4hkYAgEpg1BtmKYMeaHCRRhVAZAoFcFAABgBbEJ9z5TBdidme4Uudamw33/x3lvVvDX/+5Jk/4AENy9DnT9AAgAADSCgAAEimhEamZ6AAAAANIMAAACeOP0lagsbo6tf+07YUFQMA/KpS7eOEg5+r8O441Nal0vh+rErUph+J2JXHce01rKtLqkWs0szGpJMQ1e3BSa72xvn6tS6lv7u4Vsd2tY95nVq61aoItG5dctvK9j9R+PUtrVqmz79WSP8rBNyG5Vytd7n3D//W+5VMSoMztdXBCgAhmB9VtWiWgjgaBNMkKaGo9TQRTS7/7l+XO81hz9/vDOpBUlmIi/LBzBwQOcrcSqgsE2aOdeuZYW/v97rHn8+e+WTNbv/vip/50QPCU+Pg7HHXfBONTSU11DcdQZDviIPpHj6sPZcmxSZmCo/GpfJu1uH0ERb+qfz/X1///uZKtqPVZMR/fxDDYmUVv611S3JdmB6VMfcZTYJh2xCBVO/Ukvw3MzNmmrY1O4ciXNY0nPtxuXy5CSyVSQ0BCDACxUCwVD7MHyKcxKQ2xUDowAwC0hl/KFs1k864UZ7Zl+7XHiv2u3ub/WfMqfPuprde/b3dr3Kn/uPOGFo2LX6//uSZPCA9u9ry+czwAIAAA0g4AABEomLP+XxbcAAADSAAAAEPDDWf7tYVN9rfnqRv/LYdkMDY5brTN6mp8uztvOepMbUQqRPuNeOGAXCKfdBUqU1azrWNSUWqez/4z+FTcq+Q0kcu6qPpXtUmeOdHlb3rOpNswBTruRXUspN6u5ZfvfcsLWw8hRUeHQxJDKrNxO52TJCFMMUmcotw1j9Szhq7Zz7av1Py/OxnlZSXZ8lStYuMYJAOYficdYBecxh4RDaqPCGHBdSdoMccKbG/fuaTPpo602pup20FJsktepjBQNIFWXxonFrNnmhQY2KiJuigRpfLQzSRoXzhumgYllNJ0VEXL5icNS8XkzdZ0vgSok3rSJpa/Mz6Z9NtBZdPIrcolZzxeRM5gkgXnsvURgW0Hsuk4an0pn/+ZxYkkxBTUUzLjk5LjWqqqqqqqqqqqqqFFR0iGUAAMDPbbMN6ZBsyFGHq1qHZdG6DO5ZrTG9by53LDWsqTtSVqyJlmAoDiMCDDMJTBMDTB8uzzOzjO0JjAoC2ZR93Ij8CU8qv9w1h//7kmT2AvaMasshPstyAAANIAAAARblkzPE9k3IAAA0gAAABHmjdD7IVJaWq6enUYFwxELhtpAFE0lNWnC8ZOVXTdI4syL6eut6CK2Y6yRRKZgOw0kwOAukFHUOJK1r1tpILey1ILUgbposkXz5FzE+x04kmjbTKg0kQXY13WptN3VABEvSvx3cmQVh9rm69fOnp6e3Vjc/EIpE4tFFzsbUOLUlojBAFMFgowYKzAgWMYiww0EjYMuObtgxKUQ46A4VJWvNIbkRostZb5l/86tXx8Nasvz69McLWpQsHzqutL/88X+0sHIoI4Qh0WhwhHrQ8VD0cPsQgFg+EoAoAURWQ65rlV5+GmlmJUp1oqGcGpB0jA+Dk3FiWWNB38KhotVMQU1FMy45OS41VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVQMAEABGuCkyVFJFbLeiiJBPPrROy02HcaCRvqpSYClxmjj/+5Jk5oD1UGHNcT2DcAAADSAAAAEULW8xYfENwAAANIAAAAQAYOCn8n1LEii3IWiHZbqs0GsJhjJCa7/lAzcFCSxQtS5D9S6tUmbPa0uv44/lluFm3UsloolhK2p/przBrJP6o1qW1Tn03Zau2ydBcHJTT0cmrlgFAkaWhX/vKntr+8r/722e89/v8/u86X3a/7vxoWcRQ/B4813QQkW3KwJK22+IClXygLnWoeDZaePnUz6sGkr9lXD14zWjRd5RUkfUJms2nC2qEgJ0NP//1qeFXWKwI0SF0sRtsm3KaSkJMKlbnLCnOTejn+tmd6rMms9u07dXfvvvx/8fbh9i83af77+zce/16k33vW00RXeb6oAI+2jB7ErgGGCYEv0qAGEEPUz0dYOrYoeIxHIgMcTITDgyH30iMXliRcMSsThFx+IaRIZIdgrcTYLSJ2BvAGBxUhH45gyZwok06YzZQFqDjAI4SRq5oZmKSCamSdSroG7GJkXCKEqWzUzdN0UKenWt7ProrZBHetNWjWnskhdNm6DGaaNeiqmpbppKUrRp//uSZNAA9NRZRLE4M3IAAA0gAAABEHVrGaS8zcgAADSAAAAEpqUyWpNJk0K0bJJ6qO1bNO3MzbJWtdsaaR41pL5TJTIYHDNMKkEMUl3iPSpMKhgNxY7DokbhuclFmTwWIARXns7EAQWEAxdJgkF2JVSF9JtpEgQrTEFgsFAOYJBYjBiY/a9xL4eA0ntx40sWTJ8CPiQw6o7DGwF+n/d+/Zh+fypsSYHGEAUW8jKXEz++X+7+H34nNWe8d57pW6kt5bqYV+Y8uWt8p7GOON6vm5bhqblt1X4mDAYBgYj5dz3yk1l3W+8pq/L2tVuZZMGAgCT4LqJmX0x1jwtLtTDG1netV88q/6wt/Vr8zuY7zrVPv16mVdagcDFh7VxsbNxoFw6rvGtYrVLfNX////////////////9f9b////////////////5dFKOSWW3bX2skAbSNNFkkmGjKSCWhyt0DKQu9JpI78SZvR2oQiq8DzJjKoJoMgcFBAYhBBAAoJWFRzZ+3VgtNe25P/3LPdepGkiTKY7CBwry+4INj5gYItWqPif/7kmT/gATZX0OtYkACAAANIKAAASFeEQwZrgAAAAA0gwAAAAUE1KMU6hQPg0CiEGwLHFqLJAwuV+z1iSewYUXMjD3Ql0qlibt245GOWZXL96nu5zE/hvKMS2ALepQ80GTN/KXudTRuFX8dbg1Z/btFSYyXKHqCdkd2/NNejPNa1Sa/ueeOFnd7Gc///CNt5z/+UT0zf5h/fhgmAGsvq2r/M8e28fh9JHXPqbjFN/c6M5b//T//WCRNTMw6QAFACf50Y8hIFgyqoBZUcJVxGfMCkT5mYomzpUXSMkkkEXWyCC6K3JogSAhCBgIDgYEBYGECMB5WGAYbCAGBQAJ4IwWw0UlTSdJtaXWr+kbf9FdXTzpkRETVSqFVToIoNdDq1WVZJaKLf9/2WsV4QTN1pKtRNTUomBMkksbgo5VMjpoRc4YqNkkjcukySJQMjI0TP2UqNVV2iWMkAAH4CmzLsQBeQDA4NBzvxixNyCn5lWww1zl/DPX63hnUwx1jZwmK8gpmwKSMAAGMTxEP/F9MTgMHggSBnYRDl6dn7+5yggpJnc3/+5Jk64AHXWVQ7mOABAAADSDAAAATVZM//JqACAAANIOAAAQoK+12Osh2stjiLKQymVwQQCIiwbn0ieUshhmbkmWDhdNi6g6lqQWonjymTU6frapzpgiilsmVSiPkAMhm3RRWYLplxR0xHeRcjyPIMbHTZFI2OuylWMjV5oDxp+x5cty3apcKbUMWMQVYJQfMh/GWxykjVjKzqU4Ws6fHPvOb3UpYz273lav2A3GkTuKZigDxgmBrmsqNkYNwBIQAmFwC1ztRic9J4rdmphbF1lVG6lM7WQ1IuuYLq3TdAwk4tSjMcYD6AS8k5SYmD46joyxFjAeymReZqOpKzZI8V5NkYXUkOu2YLNkWobkDJEUOB2qFpZqmkkaUzE6RQfJAC+RYUQbZcJocSBKGKK1LT1LKRvRRSQUy+ks+o4dOr1JdvYDXe1JMx7DQqD8CIjOznJ6xN0V3V6pYq3u6y7zdXmO5bZs0Mplcpu0D10jJwgAAwHQSzAzBiNDROsxFQGQMBwjYgDdGANSCmwlkDlwqF9KYoIqQdPVVQRVdbMrYzSQM//uQZOcA9XRkTXDdk3AAAA0gAAABF62xLoR6bcgAADSAAAAESbKx91mZWDogJYxjiyYHXL5SJwmhzSdGNIaYFEmjpqcPnJi50tIE8blNM1vUtPl8yQRMespkkLwAxgFrUwJMxWpNRqouCzxxlEZI1Iwjy4gWzIyQUp0qzRalrTQTUv6RfOWL6ZkiM7wZmgHf7lRhhwMEBgM+Yl8q392ktUvZVjLO51Pw1zfM9/rC9bzsyqV3IZZGhwKoYmPg9HrP1GV4TBweo1MtZdFdWccN6lQ8zoI2dFP6no9D1nVLTROKVI0xGqA2IxLzGRmPtiKkWIeRMyICtBR0njQvutByKJpoJm6TKfW+5stZxkVKSJIwDEYM2RBZ02PbUzI8mQ8coUiLgLZVMC85Pnk2+kgp3VdH1qQWgdN01UxBTUVVVVUvTf+tZ09mxk2FRQDRhQIz0vnJfHJXTWMq8v1+WdzXf/8N8udvTWGF6Ab1t8niLcg4TzDCBj9BZTGwAwgKkTaDKren69avZNjqj6FNJSv+6N7fdNziaSSKioHsAdQ2y8W1//uSZO+B9jFsy6F+o3AAAA0gAAABFgWxM8N2bcAAADSAAAAEyKomxdcligWScNjFSjc0Tes0MTylPNjtqnTvUZn53TSFaBYQA5BtSLrMjdl5iXjM1NiBkQIKVSCOYoF5S+k6zMsN3v7XYzlQghMKEsun8kCwgYLsdwGho4CGCFQ0LxgXkiyfNUzc3MUKmRUYOkmiX3IAQcpBiAAgAgGAoCQGCgIQGHQZgBSKQNBKLAMiQSQMF4FhSI+B0kkTJePUzMzUg2yDrUl/djSyketGnnkGWZGRDTEuuklSdI2WSBudmSzdOeSdWgZmqjdRokv3agXC4tMnDzkeM4ILB8RETLVU9JVIkiGF8mycMj5mV0jNOk2prrXSSXX7oqRMj5ipVUxBTUUzLjk5LjVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVf/7kmTvgvVgbUyhPYtwAAANIAAAARYxsTN0OwAIAAA0goAABFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVQASEQAAAABBANXk0W8WcGVGVIbgBgD0mCDYXMhe8vENwAgAAkCADA0jCwLK4GGwSASHQBRYBlIkBbkMIhayBg8VeBpBRAfhRgHpl6BrwcgNPYDBoYAIDoAJQAwCFAGAH8DFwcAwCEAAgyAEHwbzg3SD6GAhYVkdIuH8LeAwoHJl4TIXAM6K8Q4kiAlE0L38S4Q8cgZYxLouUXMOEyTRqeiZf8SiGNhzxyiVSHERASMtl1VVzFFS1t/8nCwRpeFnB1wDAQBgYAhYcTg7SPKiRSUp10R1E0ZnEnb//5TMSZJz/+pMQU1FMy45OS41VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVX/+5JksYAHEGhHpkKgAAAADSDAAAAAAAGkHAAAIAAANIOAAARVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    S3 = "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lcO0MU3gC0QugylynZG6w8MekSWx+qq/f3X9AkUopB/7kI4JLh8sNasjqhZM6uqSQK0gGnYyPZvRqJ7rQEw9wShtjkPRaXeoezlPHHHVP3N0o/2ml9Na5/N46/Hn/ll+su///+rdjmvz5dieVUQAf2Z/+f///44br1P//////x5q9//7kmTggAcNZlfuPwAEAAANIMAAABwNl2f5jAAQAAA0gwAAAClMQU1FMy45OS41qqqqqqqqqqqqqqqqqqqqqqqqqgJKJEEKwAAAAAAAMpitTf4whEaNXf8WWb0NJLU/4EQmBgcCnRAXAQAQJCIDAIWD4RXRBHgRDAW9hfwHAUuDGi4R9eCAFAAB4BQLhsgYIJkwNyaIN9RaFaAYKA4GUSwKQOk0ITBZ4BADC3n8P0I4AkACRgZvZAGYCGH5jkkOD0gAQYFwoCQYCwG6uJ2E5D6CQBAQTQMHAECQtHeQwvEWIsXhCEGwENmC5oZr/lkrOUSipazqClKS6///UpE1psZGo8DKCVEHKX61GRNLpGJd//5EREgoDhHX///5dJo3IrVMQU1FMy45OS41VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVX/+5JksAAG83ZIVmKgAAAADSDAAAAAAAGkHAAAIAAANIOAAARVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
    main()
