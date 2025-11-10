#! /usr/bin/env python 
# -*- coding: utf-8 -*- 

import maica, os
import emotion_analyze_v2
t = ""
with open("token.txt", "r") as f:
    t = f.read().strip()
   
class NothingEmoSelector(emotion_analyze_v2.EmoSelector):

    def __init__(self, selector=None, storage=None, sentiment=None, eoc=None):
        super().__init__(selector, storage, sentiment, eoc)
    def get_emote(self, idle=False):
        return '1eua'
    
    def analyze(self, message):
        import re
        # 正则表达式模式
        pattern = r'\[(.*?)\]'
        # 查找所有匹配的内容
        matches = re.findall(pattern, message)
        # 处理每个匹配的内容
        for match in matches:
            # 如果匹配内容在字典的键中，去除匹配的字符串
            if match == "player":
                continue
            message = message.replace('[{}]'.format(match), '')
            
        return message

import maica_tasker
maica_tasker.default_logger = maica.logger
ai = maica.MaicaAi("SirrrrrrP", "qwerty")



ai.provider_id = 0


ai.in_mas = False

ai.sf_extraction = True
ai.MoodStatus = NothingEmoSelector()
ai.MoodStatus.main_strength = 0.0
ai.MoodStatus.repeat_strength = 0.0
ai.MoodStatus.pre_mood = ""
ai.chat_session = 0
ai.mspire_category = []
ai.target_lang = ai.MaicaAiLang.zh_cn
#ai.enable_mf = False
#ai.enable_mt = False
ai.enable_strict_mode = True
ai._ignore_accessable = True
ai.accessable()
ai._gen_token("SirrrrrrP", "qwerty", t)
ai.WSCookiesTask.enable_cookie()
print(ai.ciphertext)
print(f"{ai._verify_token()}")
print("加密完成")
ai.chat_session = 1
#ai.del_mtrigger()
ai.chat_session = 0

ai.auto_reconnect = True
print("已删除MT")
import time
data = {}
sen = {}
basedir = "e:\GithubKu\MAICA_ChatSubmod"
print(ai.get_emotion('add', "你也太可爱了!"))
#ai.init_connect()
try:
    if not ai.is_connected():
        ai.init_connect()
        while not ai.Loginer.success:
            pass

    if ai.is_in_exception():
        print("Maica ai 连接失败 {}".format(ai.is_in_exception()))
        raise Exception()
    
    if ai.is_ready_to_input():
        ai.chat("换一个发型~")
        #ai.start_MSpire()
        #ai.start_MPostal("我爱你呀~", ">3<")
        time.sleep(2.5)
    
    print("[QUEUE] status: {}, queue length: {}" .format(ai.is_responding(), ai.len_message_queue()))
    while ai.is_responding() or ai.len_message_queue() > 0:
        if ai.len_message_queue() == 0:
            time.sleep(0.5)
            continue
        message = ai.get_message()
        print("[RESPONSE] message: ", message[1])
    
    time.sleep(20)
except KeyboardInterrupt:
    print("============KeyboardInterrupt============")
finally:
    print("流程结束")
    ai.close_wss_session()

#history = ai.download_history()
#print(history)
#import json
#with open(r"E:\GithubKu\MonikaModDev-zhCN\Monika After Story\persistent_out.json",'r', encoding='utf-8') as f:
#    ai.upload_save(json.load(f))