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


ai = maica.MaicaAi("SirrrrrrP", "qwerty")



ai.provider_id = 9999


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

ai._ignore_accessable = True
ai.accessable()
ai._gen_token("SirrrrrrP", "qwerty")
print(ai.ciphertext)
print(f"{ai._verify_token()}")
print("加密完成")
import time
data = {}
sen = {}
basedir = "e:\GithubKu\MAICA_ChatSubmod"

#ai.init_connect()
try:
    if not ai.is_connected():
        ai.init_connect()
        time.sleep(3)
    if ai.is_failed():
        print("Maica ai 连接失败 {}".format(ai.status))
        raise Exception()
    
    if ai.is_ready_to_input():
        ai.chat(input("请输入内容：\n"))
        time.sleep(0.5)

    while ai.is_responding() or ai.len_message_queue() > 0:
        if ai.len_message_queue() == 0:
            time.sleep(0.5)
            continue
        message = ai.get_message()
        print("[RESPONSE] message: ", message[1])
        
except KeyboardInterrupt:
    print("============KeyboardInterrupt============")
finally:
    ai.close_wss_session()

#history = ai.download_history()
#print(history)
#import json
#with open(r"E:\GithubKu\MonikaModDev-zhCN\Monika After Story\persistent_out.json",'r', encoding='utf-8') as f:
#    ai.upload_save(json.load(f))