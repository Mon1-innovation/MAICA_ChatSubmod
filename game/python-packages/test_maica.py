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


ai = maica.MaicaAi("", "", "")
ai._gen_token(None, None, t)

ai.in_mas = False
print(ai.ciphertext)
ai.sf_extraction = True
ai.model = ai.MaicaAiModel.maica_main
ai.MoodStatus = NothingEmoSelector()
ai.MoodStatus.main_strength = 0.0
ai.MoodStatus.repeat_strength = 0.0
ai.MoodStatus.pre_mood = ""
ai.chat_session = 0
ai.mspire_category = []
ai.target_lang = ai.MaicaAiLang.zh_cn
ai.accessable()
ai.provider_id = 1
ai.init_connect()
import time
data = {}
sen = {}
basedir = "e:\GithubKu\MAICA_ChatSubmod"

try:
    
    while True:
        time.sleep(0.5)
        if ai.is_failed():
            print("Maica ai 连接失败")
            break
        if not ai.status in (ai.MaicaAiStatus.MESSAGE_WAIT_INPUT, ai.MaicaAiStatus.MESSAGE_DONE):
            #print("等待Maica返回中")
            #maica.logger.info("ai.status = {}".format(ai.status))
            time.sleep(1)
            continue
        if ai.status == ai.MaicaAiStatus.MESSAGE_DONE and len(ai.message_list) > 0:
            print("[RESPONSE] message_list.get: ", ai.message_list.get())
            continue
        if not ai.wss_session.keep_running:
            break
        #ai.status = ai.MaicaAiStatus.REQUEST_RESET_SESSION
        print("开始chat")
        ai.sf_extraction = True
        m = input("请输入内容：\n")
        if m == "":
            continue
        ai.chat(m)
        time.sleep(10.0)
        #ai.start_MSpire()
        
        
    print("wss 关闭，主进程停止")
    print(ai.MaicaAiStatus.get_description(ai.status))
    #except Exception as e:
    #    raise e
    #    print(e)
    #    print("主进程发生异常，正在停止Maica ai")
    #    ai.wss_session.close()
    #    raise e
except KeyboardInterrupt:
    ai.wss_session.close()
    print("============KeyboardInterrupt============")

#history = ai.download_history()
#print(history)
#import json
#with open(r"E:\GithubKu\MonikaModDev-zhCN\Monika After Story\persistent_out.json",'r', encoding='utf-8') as f:
#    ai.upload_save(json.load(f))