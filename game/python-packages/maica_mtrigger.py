
class MTriggerAction:
    instant = 0     #收到以后立刻触发
    post = 1        #当前轮对话结束后触发

class MTriggerExprop:
    """
    注意: 所有的值都有默认值, 如有需要请务必修改
    """
    def __init__(self, item_name_zh="", item_name_en="", item_list=[],value_limits=[0, 1], curr_value=None):
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

class MTriggerTemplate(object):
    def __init__(self, name, datakey=None):
        self.name = name
        self.datakey = datakey

common_affection_template = MTriggerTemplate("common_affection_template", "affection")
common_switch_template = MTriggerTemplate("common_switch_template", "selection")
common_meter_template = MTriggerTemplate("common_meter_template", "value")
customize_template = MTriggerTemplate("customize", None)

class MTriggerManager:
    def __init__(self):
        self.triggers = []
        self.triggered_list = []
        self._running = False
    
    def add_trigger(self, trigger):
        self.triggers.append(trigger)
    
    def build_data(self):
        self._running = False
        res = []
        for i in self.triggers:
            if i.condition():
                res.append(i.build())
        return res

    def triggered(self, name = "", param=None):
        for t in self.triggers:
            if t.name == name:
                self.triggered_list.append((t, param))

    def run_trigger(self, action=MTriggerAction.post, remove=True):
        self._running = True
        for t in self.triggered_list:
            if t[0].action == action:
                if remove:
                    self.triggered_list.remove(t)
                t[0].triggered(t[1])
        self._running = False
                

def null_callback(*args,**kwargs):
    pass

def null_condition():
    return True

class MTriggerBase(object):

    def __init__(self, template, name, usage_zh = "", usage_en = "", description = "", callback=null_callback, action=MTriggerAction.post, exprop=MTriggerExprop(), condition=null_condition):
        self.name = name
        self.usage_zh = usage_zh
        self.usage_en = usage_en
        self.template = template
        self.callback = callback
        self.action = action
        self.exprop = exprop
        self.description = description if description != "" else self.name
        self.condition = condition

    def build(self):
        return {
            "template": self.template.name,
            "name": self.name,
            "usage":{
                "zh": self.usage_zh,
                "en": self.usage_en
            },
            "exprop":{
                "item_name":{
                    "zh": self.exprop.item_name_zh,
                    "en": self.exprop.item_name_en
                },
                "item_list": self.exprop.item_list,
                "value_limits": self.exprop.value_limits,
                "curr_value": self.exprop.curr_value
            }
        }
    
    def triggered(self, data={}):
        return self.callback(data.get(self.template.datakey))