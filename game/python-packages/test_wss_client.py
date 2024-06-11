import websocket
import time
import threading


def on_open(wsapp):
    print("on_open")
    
    def send_message():
        for i in range(10):
            wsapp.send(f"Hello {i}")
            time.sleep(1)
        wsapp.close()
        
    threading.Thread(target=send_message).start()


def on_message(wsapp, message):
    print("on_message:", message)


def on_close(wsapp):
    print("on_close")


wsapp = websocket.WebSocketApp("ws://x-tool.online:8082/ws",
                               on_open=on_open,
                               on_message=on_message,
                               on_close=on_close)
print(wsapp.run_forever())
print("wtf?")

import websocket

# websocket.enableTrace(True)   # 打开日志, 将详细输出通讯过程