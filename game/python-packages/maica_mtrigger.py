import requests, json

try:
    basestring  # 套路检查
except NameError:
    basestring = str  # Python 3 统一用 str

def check_and_search(sub, target):
    if isinstance(target, basestring):
        return sub in target
    else:
        return False

class MTriggerAction:
    instant = 0     #收到以后立刻触发
    post = 1        #当前轮对话结束后触发

class MTriggerExprop:
    """
    注意: 所有的值都有默认值, 如有需要请务必修改
    """
    def __init__(self, item_name_zh="", item_name_en="", item_list=[],value_limits=[0, 1], curr_value=None, suggestion=False):
        """
        初始化函数。
        
        Args:
            item_name_zh (str): 中文选择类目的性质。
            item_name_en (str): 英文选择类目的性质。
            item_list (list): 所有可选条目的list。
            value_limits (list): 数值可取的上下限。
            curr_value (Any, optional): 当前值，默认为None。
        """
        self.item_name_zh = item_name_zh
        self.item_name_en = item_name_en
        self.item_list = item_list
        self.value_limits = value_limits
        self.curr_value = curr_value
        self.suggestion = suggestion

class MTriggerMethod:
    all = -1
    request = 0
    table = 1

class MTriggerTemplate(object):
    def __init__(self, name, datakey=None, exprop=MTriggerExprop(True,True,True,True,True,True), usage=False):
        self.name = name
        self.datakey = datakey
        self.exprop = exprop
        self.usage = usage


common_affection_template = MTriggerTemplate("common_affection_template", "affection", exprop=MTriggerExprop(False, False, False, False, False, False))
common_switch_template = MTriggerTemplate("common_switch_template", "selection", exprop=MTriggerExprop(True, True, True, False, True, True))
common_meter_template = MTriggerTemplate("common_meter_template", "value", exprop=MTriggerExprop(True, True, False, True, True, False), usage=True)
customize_template = MTriggerTemplate("customize", None, exprop=MTriggerExprop(False, False, False, False, False, False), usage=True)

class MTriggerManager:
    SIZE_LIMIT = {
        MTriggerMethod.all : 100000,
        MTriggerMethod.request : 3870,
        MTriggerMethod.table : 100000
    }
    MAX_LENGTH_REQUEST = SIZE_LIMIT[MTriggerMethod.request]
    MAX_LENGTH_TABLE = SIZE_LIMIT[MTriggerMethod.table]


    def __init__(self):
        self.triggers = []
        self.triggered_list = []
        self.enable_map = {}
        self._running = False
    
    def add_trigger(self, trigger):
        self.triggers.append(trigger)
        self.enable_map[trigger.name] = True
    
    def enable_trigger(self, name, enable=True):
        self.enable_map[name] = enable
    
    def disable_trigger(self, name):
        self.enable_trigger(name, False)
    
    def output_settings(self):
        return self.enable_map
    
    def import_settings(self, settings):
        for k, v in settings.items():
            self.enable_map[k] = v
    
    def remove_trigger(self, name):
        for i in self.triggers:
            if i.name == name:
                self.triggers.remove(i)


    def trigger_status(self, name):
        return self.enable_map[name] if name in self.enable_map else False
    

    def build_data(self, method=MTriggerMethod.all, full = False):
        self.triggered_list = []
        self._running = False
        res = []
        for i in self.triggers:
            if i.condition() and self.trigger_status(i.name) and (i.method == method or method == MTriggerMethod.all):
                if len(res) + len(i) > self.SIZE_LIMIT[method] and not full:
                    self.disable_trigger(i.name)
                    continue
                res.append(i.build())
        return res

    def send_to_table(self, token, session, data):
        req = {
            "access_token": token,
            "chat_session": session,
            "content": data
        }
        res = requests.post("https://maicadev.monika.love/api/trigger", json=req)
        return res
        

    def get_length(self, method=MTriggerMethod.all):
        return len(json.dumps(self.build_data(method=method, full=True), ensure_ascii=False))

    def triggered(self, name = "", param=None):
        for t in self.triggers:
            if t.name == name:
                self.triggered_list.append((t, param))

    def run_trigger(self, action=MTriggerAction.post, remove=True):
        doact = {
            "stop":False,
        }
        self._running = True
        for t in self.triggered_list:


            if t[0].action == action:
                if remove:
                    self.triggered_list.remove(t)
                res = t[0].triggered(t[1])
                if check_and_search("stop", res):
                    doact["stop"] = True

        self._running = False
        return doact
                

def null_callback(*args,**kwargs):
    pass

def null_condition():
    return True

class MTriggerBase(object):

    def __init__(self, template, name, usage_zh = "", usage_en = "", description = "", callback=null_callback, action=MTriggerAction.post, exprop=MTriggerExprop(), condition=null_condition, method=MTriggerMethod.request, perf_suggestion = False):
        self.name = name
        self.usage_zh = usage_zh
        self.usage_en = usage_en
        self.template = template
        self.callback = callback
        self.action = action
        self.exprop = exprop
        self.description = description if description != "" else self.name
        self.condition = condition
        self.method = method
        self.perf_suggestion = perf_suggestion

    def build(self):
        data = {
            "template": self.template.name,
            "name": self.name,
            "exprop":{
            }
        }

        if self.template.usage:
            data["usage"] = {
                "zh": self.usage_zh,
                "en": self.usage_en
            }
        if self.template.exprop.suggestion:
            data["exprop"]["suggestion"] = self.exprop.suggestion
        if self.template.exprop.item_name_zh:
            data["exprop"]["item_name"] = {"zh": self.exprop.item_name_zh, "en": self.exprop.item_name_en} 
        if self.template.exprop.item_list:
            data["exprop"]["item_list"] = self.exprop.item_list
        if self.template.exprop.value_limits:
            data["exprop"]["value_limits"] = self.exprop.value_limits
        if self.template.exprop.curr_value:
            data["exprop"]["curr_value"] = self.exprop.curr_value
        if data["exprop"] == {}:
            del data["exprop"]
        return data

    
    def triggered(self, data={}):
        value = data.get(self.template.datakey) if self.template.datakey else None
        if self.perf_suggestion and "suggestion" in data:
            return self.callback(data.get("suggestion"))
        if not value and self.template.exprop.suggestion and "suggestion" in data:
            value = data.get("suggestion")
        return self.callback(value)

    def __len__(self):
        return len(json.dumps(self.build(), ensure_ascii=False))