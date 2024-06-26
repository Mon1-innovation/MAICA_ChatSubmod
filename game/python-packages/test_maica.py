import maica
import emotion_analyze
ai = maica.MaicaAi("", "", "")

print(ai.ciphertext)
ai.sf_extraction = True
ai.model = ai.MaicaAiModel.maica_main
ai.chat_session
ai.init_connect()
import time
print("读取表情信息")
data = {}
sen = {}
with open(r"E:\GithubKu\MAICA_ChatSubmod\game\Submods\MAICA_ChatSubmod\emotion_sentiment.txt", "r", encoding="utf-8") as s:
    for i in s.readlines():
        line = i.split(":")
        line[1] = line[1].strip()
        sen[line[0]] = line[1]
emotion_analyze.add_emoteeffectdata(sen)
with open(r"E:\GithubKu\MAICA_ChatSubmod\game\Submods\MAICA_ChatSubmod\emotion.txt", "r", encoding="utf-8") as e:
    for i in e.readlines():
        line = i.split(":")
        line[1] = line[1].strip()
        if line[1] not in data:
            data[line[1]] = {"sentiment":sen[line[1] if line[1] in sen else 0]}
        if not len(line[0]) in data[line[1]]:
            data[line[1]][len(line[0])] = []
        data[line[1]][len(line[0])].append(line[0])
    
    for i in data:
        for n in i:
            n = set(n)

    print(data)

emotion_analyze.add_emotedata(data)

try:
    try:
        while True:
            if not ai.status in (ai.MaicaAiStatus.MESSAGE_WAIT_INPUT, ai.MaicaAiStatus.MESSAGE_DONE):
                print("等待Maica返回中")
                maica.logger.info(f"ai.status = {ai.status}:{ai.MaicaAiStatus.get_description(ai.status)}")
                time.sleep(1)
                continue
            if ai.status == ai.MaicaAiStatus.MESSAGE_DONE and len(ai.message_list.queue) > 0:
                print("message_list.get: ", ai.message_list.get())
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
        print("wss 关闭，主进程停止")
    except Exception as e:
        print(e)
        print("主进程发生异常，正在停止Maica ai")
        ai.wss_session.close()
        raise e
except KeyboardInterrupt:
    ai.wss_session.close()
    print("============KeyboardInterrupt============")
#import json
#with open(r"E:\GithubKu\MonikaModDev-zhCN\Monika After Story\persistent_out.json",'r', encoding='utf-8') as f:
#    ai.upload_save(json.load(f))