import maica

ai = maica.MaicaAi("", "", "hDtIuFWP5XnEXQIOZZBambwkRsBKqkzW//ZtELrPHm/wEXdxqW3PBXOPHKbZg6URYED+HcznHOyAFRefhXiZNkPOBpxjfpnbsT40UHdcPvaYVFfRTOfS+cAMChxoVESHuJTmXJzKzAECrmHBxMG6u6FZI6VHyr1RjrFKUcS1OSxjMfNoqspFN/mQNsgQawaV2kmmOUrikTF7JaHCBSC1SnA5SdDsrXf15Ez4Q==")

print(ai.ciphertext)

ai.init_connect()
import time
while ai.status != ai.MaicaAiStatus.MESSAGE_WAIT_INPUT:
    print("等待input")
    time.sleep(1)
print("开始chat")
ai.sf_extraction = True
ai.chat("我的生日是什么时候来着？")
#import json
#ai.upload_save(json.dumps({
#    "mas_playername": "pp",
#    "mas_player_bday": [2001, 1, 1],
#    "mas_affection": 2000 
#}))