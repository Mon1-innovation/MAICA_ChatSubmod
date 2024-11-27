# MTrigger

Blessland provides full support for MAICA MTrigger. By importing the `maica_mtrigger.py` file, you can use MTrigger functionality.

## Creating an MTrigger

```python
from maica_mtrigger import *

example_mtrigger = MTriggerBase(
    template,
    name,
    usage_zh="",
    usage_en="",
    description="",
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

Parameter explanation:

* `template` **Required**  
  * The template being used. Currently available templates include `common_affection_template` (Generic Affection), `common_switch_template` (Generic Switch), `common_meter_template` (Generic Adjustment), `customize_template` (Custom Template).

  * `common_affection_template`
    * This template triggers decisions on how to adjust affection based on user input and previous content.
    * No parameters are needed for `exprop` with this template.
    * When using this template, `name` must be `alter_affection`.

  * `common_switch_template`
    * Allows selection based on categories provided by the user.
    * `name` and `MTriggerExprop` must be named according to the intended use of the categories.
    * Under this template, `MTriggerExprop` considers `item_name_zh`, `item_name_en`, `item_list`, and `curr_value`.
    * If `item_list` exceeds 72, 72 items will be randomly selected by the backend.
    * If there are more than 6 `common_switch_template`s, 6 will be randomly selected by the backend.

  * `common_meter_template`
    * Template for adjusting numerical values.
    * `name` and `MTriggerExprop` must be named according to the intended use of the categories.
    * Under this template, `MTriggerExprop` considers `item_name_zh`, `item_name_en`, `value_limits`, and `curr_value`.
    * If there are more than 6 `common_switch_template`s, 6 will be randomly selected by the backend.

  * `customize_template`
    * A custom template where the model decides whether to trigger it.
    * `exprop` parameters are not considered for this template.
    * If there are more than 20 `customize_template`s, 20 will be randomly selected by the backend.

* `name` **Required**
  * The name of the trigger. It can be freely named except for in `common_affection_template`, and it is recommended to indicate its purpose as clearly as possible.

* `usage_zh`, `usage_en`
  * Instructions for using the trigger in Chinese and English, only used under `customize_template`.

* `description`
  * Description of the trigger for local reference only, not involved in model operation.

* `callback`
  * Callback function of the trigger, default is `null_callback`. It is executed when the trigger is activated.
  * This function has one parameter representing the value chosen by the model.
  * **The parameter may not be of the expected type and is not guaranteed to be a value set in `exprop`, so validation is required.**
  * This action will not automatically hide the console. To control console display (e.g., if using a jump), call the labels `maica_show_console` and `maica_hide_console` for related operations.
  * In the callback, using operations like call or jump may lead to packet loss in the next round of conversation. Please call the label `maica_reconnect` to avoid such situations.

* `action`
  * The trigger executes an action, defaulting to `MTriggerAction.post`.
    * `MTriggerAction.post` is a post-trigger that activates after a conversation round is complete.
    * ~~`MTriggerAction.instant` triggers immediately, executing the trigger as soon as the model activates it~~ No longer recommended.
        > Note: This trigger cannot execute `renpy.call` or other renpy statements.
        
        > Note: Due to backend changes, the `instant` trigger will execute after the main model response is completed, making `post` and `instant` essentially identical in behavior.


* `exprop`
  * Properties of the trigger, with default values as in the above code.
    * `item_name_zh`, `item_name_en`
      * The nature of the selected category in Chinese and English.
    * `item_list`
      * All available options, provided as a list.
    * `value_limits`
      * Value range.
    * `curr_value`
      * Current value.

* `condition`
  * The condition for the trigger, default is `null_condition`. The trigger is only submitted to the model if the `condition` function returns `True`. By default, it always returns True.

To use this trigger, add `example_mtrigger` to the `Maica` instance:

```python
maica_instance.mtrigger_manager.add_trigger(example_mtrigger)
```

You can find the `Maica` instance using:

```python
maica_instance = store.maica.maica
```