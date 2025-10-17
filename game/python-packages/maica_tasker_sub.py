from maica_tasker import *

class GeneralWsErrorHandler(MaicaWSTask):
    def __init__(self, task_type, name, except_ws_types=..., logger = None):
        super().__init__(task_type, name, except_ws_types)
        self.logger = logger

    def on_received(self, event):
        if event.event_type != MAICATASK_TYPE_WS:
            return
        else:
            wspack = event.data
            if wspack.type == 'error' or 500 <= wspack.code <= 600:
                event.manager.close_ws()
                if self.logger:
                    self.logger.error("[GeneralWsErrorHandler] websocket error: " + event.content + "\nwebsocket connection closed")


class GeneralWsLogger(MaicaWSTask):
    def __init__(self, task_type, name, except_ws_types=..., logger = None):
        super().__init__(task_type, name, except_ws_types)
        self.logger = logger

    def on_received(self, event):
        if event.event_type != MAICATASK_TYPE_WS:
            return
        else:
            wspack = event.data
            if self.logger:
                if wspack.type == 'info':
                    self.logger.info("[GeneralWsLogger] " + "<{}> {}".format(wspack.status, wspack.content))
                elif wspack.type == 'warn':
                    self.logger.warning("[GeneralWsLogger] " + "<{}> {}".format(wspack.status, wspack.content))
                elif wspack.type == 'error':
                    self.logger.error("[GeneralWsLogger] " + "<{}> {}".format(wspack.status, wspack.content))
                else:
                    self.logger.debug("[GeneralWsLogger] " + "<{}> {}".format(wspack.status, wspack.content))

class HistoryStatusHandler(MaicaWSTask):
    TOKEN_24000_EXCEEDED = 1
    TOKEN_MAX_EXCEEDED = 2
    def __init__(self, task_type, name):
        super().__init__(task_type, name, except_ws_types = ['maica_history_slice_hint', 'maica_history_sliced'])

    def on_received(self, ws):
        if ws.type == 'maica_history_slice_hint':
            self.status = self.TOKEN_24000_EXCEEDED
        elif ws.type == 'maica_history_sliced':
            self.status = self.TOKEN_MAX_EXCEEDED

class MAICAUserDataHandler(MaicaWSTask):
    def __init__(self, task_type, name):
        super().__init__(task_type, name, except_ws_types = ['maica_login_user', 'maica_login_id', 'maica_login_nickname'])
        self.id = None
        self.nickname = None
        self.account = None

    def on_received(self, ws):
        if ws.type == 'maica_login_user':
            self.account = ws.content
        elif ws.type == 'maica_login_id':
            self.id = ws.content
        elif ws.type == 'maica_login_nickname':
            self.nickname = ws.content

class MTriggerWsHandler(MaicaWSTask):
    def __init__(self, task_type, name, mt_manager):
        super().__init__(task_type, name, except_ws_types = ['maica_mtrigger_trigger'])
        self.manager = mt_manager

    def on_received(self, ws):
        if ws.type == 'maica_mtrigger_trigger':
            import json
            from maica_mtrigger import MTriggerAction

            data = json.loads(ws.content)
            for item in data:
                self.manager.triggered(item, data[item])
            self.manager.run_trigger(MTriggerAction.instant)

class MAICAWSCookiesHandler(MaicaWSTask):
    def __init__(self, task_type, name):
        super().__init__(task_type, name, except_ws_types = ['maica_connection_security_cookie'])
        self.cookie = None

    def on_received(self, ws):
        if ws.type == 'maica_connection_security_cookie':
            self.cookie = ws.content
import json
class MAICALoginTasker(MaicaWSTask):

    def on_manual_run(self, manager, token):
        data = json.dumps({
            'accesstoken': token
        })
        manager.ws_client.send(data)
    
    def login(token):
        super().start_event(token)