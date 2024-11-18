# MTrigger

Blessland提供了完整的MAICA MTrigger支持, 通过导入maica_mtrigger.py文件, 即可使用MTrigger功能

## 创建一个MTrigger

```python
from maica_mtrigger import *

example_mtrigger = MTriggerBase(
    template,
    name,
    usage_zh="",
    usage_en="",
    description = "",
    callback=null_callback,
    action=MTriggerAction.post,
    exprop=MTriggerExprop(
        item_name_zh="",
        item_name_en="",
        item_list=[],
        value_limits=[0, 1],
        curr_value=None
    ),
    condition=null_condition
)

```

参数解析：

* `template` **必填**  
  * 所使用的template模板, 目前有`common_affection_template`(通用好感度), `common_switch_template`(通用选择模板), `common_meter_template`(通用调整模板), `customize_template`(自定义模板)
  

  * `common_affection_template`
    * 该模板的触发器会根据用户输入与上文内容, 决策对好感度应做的调整.
    * 该模板下`MTriggerExprop`仅考虑`value_limits`
    * 使用该模板, `name`必须为`alter_affection`

  * `common_switch_template`
    * 根据用户所给出的类目进行选择
    * `name`, `MTriggerExprop`的命名必须符合所给类目的用途.
    * 该模板下`MTriggerExprop`考虑`item_name_zh`, `item_name_en`, `item_list`, `curr_value`
  
  * `common_meter_template`
    * 用于调整数值的模板
    * `name`, `MTriggerExprop`的命名必须符合所给类目的用途.
    * 模板下`MTriggerExprop`考虑`item_name_zh`, `item_name_en`, `value_limits`, `curr_value`
  
  * `customize_template`
    * 自定义模板, 由模型自行选择是否触发
    * 该模板不考虑`exprop`参数

* `name` **必填**
  * 触发器名称, 除`common_affection_template`外, 可以自由命名, 建议尽可能表明用途

* `usage_zh`, `usage_en`
  * 触发器使用说明, 中英文, 仅在`customize_template`下使用
  
* `description`
  * 触发器描述, 仅用于本地参考, 不参与模型运行

* `callback`
  * 触发器回调函数, 默认为`null_callback`, 当触发器触发时, 执行该函数
  * 该函数有一个入参, 表示模型所选择的值
  * 入参并不一定是你所期待的类型, 建议对其进行显式转换
  
* `action`
  * 触发器执行动作, 默认为`MTriggerAction.post`
    * `MTriggerAction.post`为后置触发, 一轮对话完毕后触发
    * `MTriggerAction.instant`为立刻触发, 当模型触发该触发器时, 立刻执行该触发器
        > 注意: 该触发器无法执行`renpy.call`等renpy语句

  
* `exprop`
  * 触发器属性, 默认值为上述代码中的值
    * `item_name_zh`, `item_name_en`
      * 所选类目的性质, 中英文
    * `item_list`
      * 所有的可选项, 此为list
    * `value_limits`
      * 取值范围
    * `curr_value`
      * 当前值

* `condition`
  * 触发器条件, 默认为`null_condition`, 只有当`condition`的函数返回为`True`时, 触发器才会提交给模型. 默认情况下将永远返回True

通过将`example_mtrigger`添加到`Maica`实例中即可使用该触发器：

```python
maica_instance.mtrigger_manager.add_trigger(clothes_trigger)
```

你可以用以下方式找到`Maica`实例

```python
maica_instance = store.maica.maica
```
