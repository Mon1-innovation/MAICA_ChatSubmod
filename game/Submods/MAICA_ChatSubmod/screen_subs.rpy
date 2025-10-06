
screen maica_log():
    python:
        submods_screen = store.renpy.get_screen("submods", "screens")
        maica_log = store.maica.update_info
        persistent._maica_updatelog_version_seen = maica_log.get("version", persistent._maica_updatelog_version_seen)
        if submods_screen:
            _tooltip = submods_screen.scope.get("tooltip", None)
        else:
            _tooltip = None
        def set_provider(id):
            persistent.maica_setting_dict["provider_id"] = int(id)

    modal True
    zorder 92
    
    use maica_common_outer_frame():
        use maica_common_inner_frame():
            style_prefix "generic_fancy_check"
            
            use divider_small(maica_log.get("title"))

            for content in maica_log.get("content"):
                text content.replace("[", "[[").replace("{", "{{").replace("【", "【【"):
                    size 18
                use divider_plain_small()
        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("关闭"):
                action Hide("maica_log")

screen maica_tz_setting():
    python:
        # 从-12开始
        store.timezone_dict = {
            -12: "Etc/GMT+12",
            -11: "Pacific/Midway",
            -10: "Pacific/Honolulu",
            -9: "America/Anchorage",
            -8: "America/Los_Angeles",
            -7: "America/Denver",
            -6: "America/Chicago",
            -5: "America/New_York",
            -4: "America/Indiana/Vincennes",
            -3: "America/Argentina/Buenos_Aires",
            -2: "Atlantic/South_Georgia",
            -1: "Atlantic/Azores",
            0: "Europe/London",
            1: "Europe/Berlin",
            2: "Europe/Kaliningrad",
            3: "Europe/Moscow",
            4: "Asia/Dubai",
            5: "Asia/Karachi",
            6: "Asia/Dhaka",
            7: "Asia/Bangkok",
            8: "Asia/Shanghai",
            9: "Asia/Tokyo",
            10: "Australia/Sydney",
            11: "Pacific/Noumea",
            12: "Pacific/Auckland",
            13: "Pacific/Tongatapu",
            14: "Pacific/Kiritimati"
        }
        store.timezone_list = sorted(list(store.timezone_dict.keys()))
        def get_gmt_offset_timezone():
            import time
            import sys

            # 获取当前本地时间的 UTC 偏移量（以秒为单位）
            if time.localtime().tm_isdst:
                offset_sec = -time.altzone
            else:
                offset_sec = -time.timezone

            # 将偏移量转换为小时
            offset_hours = offset_sec // 3600
            return store.timezone_dict[offset_hours]

        current_tz = get_gmt_offset_timezone()

    modal True
    zorder 92
    
    use maica_common_outer_frame():
        use maica_common_inner_frame():
            style_prefix "generic_fancy_check"
            
            text _("{size=-10}如果这里没有你的时区, 请根据你当地的UTC时间选择")
            
            hbox:
                style_prefix "maica_check"
                textbutton _("根据语言自动选择"):
                    action SetDict(persistent.maica_setting_dict, "tz", 'Asia/Shanghai' if store.maica.maica.target_lang == store.maica.maica.MaicaAiLang.zh_cn else 'America/Indiana/Vincennes')
            
            hbox:
                style_prefix "maica_check"
                textbutton _("根据系统时区自动选择"):
                    action SetDict(persistent.maica_setting_dict, "tz", current_tz)

            for item in timezone_list:
                hbox:
                    textbutton "UTC" + "{}".format("+" if item >= 0 else "") + str(item) + "|" + timezone_dict[item]:
                        action SetDict(persistent.maica_setting_dict, "tz", timezone_dict[item])
        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("关闭"):
                action Hide("maica_tz_setting")


screen maica_advance_setting():
    $ _tooltip = store._tooltip
    python:
        def reset_to_default():
            for item in store.maica.maica.default_setting:
                if item == 'seed':
                    store.maica.maica.default_setting[item] = 0
                if item in persistent.maica_advanced_setting:
                    persistent.maica_advanced_setting[item] = store.maica.maica.default_setting[item]
                    persistent.maica_advanced_setting_status[item] = False

    modal True
    zorder 92
    
    use maica_common_outer_frame():
        use maica_common_inner_frame():
            style_prefix "generic_fancy_check"
            hbox:
                style_prefix "maica_check"
                text _("关于这些参数的详细解释, 参见 "):
                    size 20
                textbutton _("{u}MAICA 官方文档{/u}"):
                    action OpenURL("https://github.com/Mon1-innovation/MAICA/blob/main/document/API%20Document.txt")
                    text_size 20
                text _(" 和 "):
                    size 20
                textbutton _("{u}OpenAI 中文文档{/u}"):
                    action OpenURL("https://www.openaidoc.com.cn/api-reference/chat" if config.language == "chinese" else "https://platform.openai.com/docs/api-reference/completions/create#completions_create")
                    text_size 20
            hbox:
                text _("{size=-10}注意: 只有被勾选的高级参数才会被使用, 未勾选的参数将使用服务端默认设置")
            hbox:
                if not persistent.maica_setting_dict.get('use_custom_model_config'):
                    text _("{size=-10}你当前未启用'使用高级参数', 该页的所有设置都不会生效!")

            use divider_small(_("超参数"))
            $ sdict = "maica_advanced_setting"

            hbox:
                spacing 5
                textbutton "top_p":
                    action ToggleDict(persistent.maica_advanced_setting_status, "top_p")
                    hovered SetField(_tooltip, "value", _("token权重过滤范围. 非常不建议动这个"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                
                if persistent.maica_advanced_setting_status.get("top_p", False):
                    use prog_bar("top_p", 250, _("token权重过滤范围. 非常不建议动这个"), "top_p", 0.1, 1.0, sdict=sdict)

            hbox:
                spacing 5
                textbutton "temperature":
                    action ToggleDict(persistent.maica_advanced_setting_status, "temperature")
                    hovered SetField(_tooltip, "value", _("token选择的随机程度. 数值越高, 模型输出会越偏离普遍最佳情况"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("temperature", False):
                    use prog_bar("temperature", 250, _("token选择的随机程度. 数值越高, 模型输出会越偏离普遍最佳情况"), "temperature", 0.0, 1.0, sdict=sdict)

            hbox:
                spacing 5
                textbutton "max_tokens":
                    action ToggleDict(persistent.maica_advanced_setting_status, "max_tokens")
                    hovered SetField(_tooltip, "value", _("模型一轮生成的token数限制. 一般而言不会影响表现, 只会截断超长的部分"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)

                if persistent.maica_advanced_setting_status.get("max_tokens", False):
                    use prog_bar("max_tokens", 250, _("模型一轮生成的token数限制. 一般而言不会影响表现, 只会截断超长的部分"), "max_tokens", 1, 2048, sdict=sdict)

            hbox:
                spacing 5
                textbutton "frequency_penalty":
                    action ToggleDict(persistent.maica_advanced_setting_status, "frequency_penalty")
                    hovered SetField(_tooltip, "value", _("token频率惩罚. 数值越高, 反复出现的token越不可能继续出现, 一般会产生更短且更延拓的结果"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("frequency_penalty", False):
                    use prog_bar("frequency_penalty", 250, _("token频率惩罚. 数值越高, 反复出现的token越不可能继续出现, 一般会产生更短且更延拓的结果"), "frequency_penalty", 0.0, 1.0, sdict=sdict)

            hbox:
                spacing 5
                textbutton "presence_penalty":
                    action ToggleDict(persistent.maica_advanced_setting_status, "presence_penalty")
                    hovered SetField(_tooltip, "value", _("token重现惩罚. 数值越高, 出现过的token越不可能再次出现, 一般会产生更跳跃的结果"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("presence_penalty", False):
                    use prog_bar("presence_penalty", 250, _("token重现惩罚. 数值越高, 出现过的token越不可能再次出现, 一般会产生更跳跃的结果"), "presence_penalty", 0.0, 1.0, sdict=sdict)

            hbox:
                spacing 5
                if not persistent.maica_setting_dict.get('42seed'):
                    textbutton "seed":
                        action ToggleDict(persistent.maica_advanced_setting_status, "seed")
                        hovered SetField(_tooltip, "value", _("生成种子. 一般而言影响很小且随机"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)
                    if persistent.maica_advanced_setting_status.get("seed", False):
                        use num_bar("seed", 200, _("生成种子. 一般而言影响很小且随机"), "seed", -2147483648, 2147483647, sdict=sdict)
                else:
                    textbutton "seed ":
                        action NullAction()
                        hovered SetField(_tooltip, "value", _("! 最佳实践已启用, 种子锁定为42"))
                        unhovered SetField(_tooltip, "value", _tooltip.default)
                        selected persistent.maica_advanced_setting_status.get('seed', False)

            use divider_small(_("高级设置"))

            hbox:
                spacing 5
                textbutton "tnd_aggressive":
                    action ToggleDict(persistent.maica_advanced_setting_status, "tnd_aggressive")
                    hovered SetField(_tooltip, "value", _("即使MFocus未调用工具, 也提供一些工具的结果.\n+ 其值越高, 越能避免信息缺乏导致的幻觉, 并产生灵活体贴的表现\n- 其值越高, 越有可能产生注意力涣散和专注混乱"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("tnd_aggressive", False):
                    use num_bar("tnd_aggressive", 200, _("即使MFocus未调用工具, 也提供一些工具的结果.\n+ 其值越高, 越能避免信息缺乏导致的幻觉, 并产生灵活体贴的表现\n- 其值越高, 越有可能产生注意力涣散和专注混乱"), "tnd_aggressive", 0, 3, sdict=sdict)

            hbox:
                spacing 5
                textbutton "mf_aggressive:[persistent.maica_advanced_setting.get('mf_aggressive', 'None')]":
                    action [ToggleDict(persistent.maica_advanced_setting_status, "mf_aggressive"),
                        ToggleDict(persistent.maica_advanced_setting, "mf_aggressive")]
                    hovered SetField(_tooltip, "value", _("要求agent模型生成最终指导, 并替代默认MFocus指导.\n+ 信息密度更高, 更容易维持语言自然\n- 表现十分依赖agent模型自身的能力\n- 启用时一般会无效化tnd_aggressive"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected persistent.maica_advanced_setting_status.get('mf_aggressive')
            hbox:
                spacing 5
                textbutton "sfe_aggressive:[persistent.maica_advanced_setting.get('sfe_aggressive', 'None')]":
                    action [ToggleDict(persistent.maica_advanced_setting_status, "sfe_aggressive"),
                        ToggleDict(persistent.maica_advanced_setting, "sfe_aggressive")]
                    hovered SetField(_tooltip, "value", _("将prompt和引导中的[[player]字段替换为玩家真名.\n+ 模型对玩家的名字有实质性理解\n- 明显更容易发生表现离群和专注混乱"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected persistent.maica_advanced_setting_status.get('sfe_aggressive')
            hbox:
                spacing 5
                textbutton "esc_aggressive:[persistent.maica_advanced_setting.get('esc_aggressive', 'None')]":
                    action [ToggleDict(persistent.maica_advanced_setting_status, "esc_aggressive"),
                        ToggleDict(persistent.maica_advanced_setting, "esc_aggressive")]
                    hovered SetField(_tooltip, "value", _("在MFocus调用互联网搜索的情况下, 要求其整理一遍结果.\n+ 大多数情况下信息密度更高, 更容易维持语言自然\n- 涉及互联网搜索时生成速度更慢"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected persistent.maica_advanced_setting_status.get('esc_aggressive')
            hbox:
                spacing 5
                textbutton "amt_aggressive: [persistent.maica_advanced_setting.get('amt_aggressive', 'None')]":
                    action [ToggleDict(persistent.maica_advanced_setting_status, "amt_aggressive"),
                        ToggleDict(persistent.maica_advanced_setting, "amt_aggressive")]
                    hovered SetField(_tooltip, "value", _("当MTrigger存在时, 要求MFocus预检玩家的请求并提供指导.\n+ 比较明显地改善MTrigger失步问题\n- 在少数情况下对语言的自然性产生破坏\n* 当对话未使用MTrigger或仅有好感触发器, 此功能不会生效"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected persistent.maica_advanced_setting_status.get('amt_aggressive')
            hbox:
                spacing 5
                textbutton "nsfw_acceptive:[persistent.maica_advanced_setting.get('nsfw_acceptive', 'None')]":
                    action [ToggleDict(persistent.maica_advanced_setting_status, "nsfw_acceptive"),
                        ToggleDict(persistent.maica_advanced_setting, "nsfw_acceptive")]
                    hovered SetField(_tooltip, "value", _("要求模型宽容正面地对待有毒内容.\n+ (出乎意料地)在大多数场合下对模型表现有正面作用, 即使不涉及有毒内容\n- 在少数情况下造成意料之外的问题"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                    selected persistent.maica_advanced_setting_status.get('nsfw_acceptive')

            hbox:
                spacing 5
                textbutton "pre_additive":
                    action ToggleDict(persistent.maica_advanced_setting_status, "pre_additive")
                    hovered SetField(_tooltip, "value", _("在MFocus介入时, 额外提供上下文以供分析. 范围0-5.\n+ 改善MFocus对连贯对话的理解能力\n- 明显更容易破坏MFocus的应答模式"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("pre_additive", False):
                    use num_bar("pre_additive", 200, _("在MFocus介入时, 额外提供上下文以供分析. 范围0-5.\n+ 改善MFocus对连贯对话的理解能力\n- 明显更容易破坏MFocus的应答模式"), "pre_additive", 0, 5, sdict=sdict)

            hbox:
                spacing 5
                textbutton "post_additive":
                    action ToggleDict(persistent.maica_advanced_setting_status, "post_additive")
                    hovered SetField(_tooltip, "value", _("在MTrigger介入时, 额外提供上下文以供分析. 范围0-5.\n+ 改善MTrigger对连贯对话的理解能力\n- 更容易破坏MTrigger的应答模式"))
                    unhovered SetField(_tooltip, "value", _tooltip.default)
                if persistent.maica_advanced_setting_status.get("post_additive", False):
                    use num_bar("post_additive", 200, _("在MTrigger介入时, 额外提供上下文以供分析. 范围0-5.\n+ 改善MTrigger对连贯对话的理解能力\n- 更容易破坏MTrigger的应答模式"), "post_additive", 0, 5, sdict=sdict)


        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("保存设置"):
                action [
                    Hide("maica_advance_setting"),
                    Function(renpy.notify, _("MAICA: 已保存高级设置"))
                ]
            textbutton _("重置设置"):
                action [
                    Function(reset_to_default),
                    Hide("maica_advance_setting"),
                    Function(renpy.notify, _("MAICA: 已重置高级设置") if store.maica.maica.is_accessable() else _("MAICA: 已重置高级设置(缺省值)"))
                ]


screen maica_select_language():
    modal True
    zorder 92

    use maica_setter_small_frame(ok_action=Hide("maica_select_language")):
        style_prefix "generic_fancy_check"
        hbox:
            textbutton _("zh | 简体中文"):
                action SetDict(persistent.maica_setting_dict, "target_lang", store.maica.maica.MaicaAiLang.zh_cn)
        hbox:
            textbutton _("en | English"):
                action SetDict(persistent.maica_setting_dict, "target_lang", store.maica.maica.MaicaAiLang.en)
       

default use_email = True
screen maica_login():
    modal True
    zorder 92

    $ ok_action = [
                    Function(store.maica.maica._gen_token, store._maica_LoginAcc, store._maica_LoginPw, "", store._maica_LoginEmail if store._maica_LoginEmail != "" else None),
                    Function(_maica_verify_token),
                    Function(_maica_clear), 
                    Hide("maica_login")
                    ]
    $ cancel_action = [Function(_maica_clear), Hide("maica_login")]

    use maica_setter_medium_frame(ok_action=ok_action, cancel_action=cancel_action):

        hbox:
            if use_email:
                textbutton _("输入DCC账号邮箱"):
                    style "confirm_button"
                    action Show("maica_login_input",message = _("请输入DCC账号邮箱"),returnto = "_maica_LoginEmail")
            else:
                textbutton _("输入DCC账号用户名"):
                    style "confirm_button"
                    action Show("maica_login_input",message = _("请输入DCC账号用户名") ,returnto = "_maica_LoginAcc")

        hbox:
            style_prefix "maica_check"
            if use_email:
                textbutton _("> 改为用户名登录"):
                    text_size 15
                    action [ToggleVariable("use_email"), Function(_maica_clear)]
                    selected False

            else:
                textbutton _("> 改为邮箱登录"):
                    text_size 15
                    action [ToggleVariable("use_email"), Function(_maica_clear)]
                    selected False

        hbox:
            textbutton _("输入密码"):
                style "confirm_button"
                action Show("maica_login_input",message = _("请输入密码"),returnto = "_maica_LoginPw")
        hbox:
            text ""
        # hbox:
        #     textbutton _("连接至服务器生成MAICA令牌"):
        #         action [
        #             Function(store.maica.maica._gen_token, store._maica_LoginAcc, store._maica_LoginPw, "", store._maica_LoginEmail if store._maica_LoginEmail != "" else None),
        #             Function(_maica_verify_token),
        #             Function(_maica_clear), 
        #             Hide("maica_login")
        #             ]
        #     textbutton _("取消"):
        #         action [Function(_maica_clear), Hide("maica_login")]
        hbox:
            style_prefix "small_expl"
            text _("※ 使用MAICA Blessland, 即认为你同意 "):
                size 15
            textbutton _("{u}MAICA服务条款{/u}"):
                action OpenURL("https://maica.monika.love/tos")
                yalign 1.0

        hbox:
            style_prefix "small_expl"
            text _("※ 还没有DCC账号? "):
                size 15
            textbutton _("{u}注册一个{/u}"):
                action OpenURL("https://maica.monika.love/tos")
                yalign 1.0


screen maica_login_input(message, returnto, ok_action = Hide("maica_login_input")):
    ## Ensure other screens do not get input while this screen is displayed.s
    modal True
    zorder 92

    use maica_setter_small_frame(message, ok_action):
        input default "" value VariableInputValue(returnto) length 64

screen maica_addition_input(addition="", edittarget=None):
    python:
        if persistent._mas_player_addition == None:
            persistent._mas_player_addition = ""
        def apply(edittarget):
            addition = "[player]" + persistent._mas_player_addition
            if not persistent._mas_player_addition.strip():
                return
            if addition in persistent.mas_player_additions:
                return
            if edittarget:
                persistent.mas_player_additions[persistent.mas_player_additions.index(edittarget)] = addition
            else:
                persistent.mas_player_additions.append(addition)
            del persistent._mas_player_addition
        def paste(content=None):
            if not content:
                content = (pygame.scrap.get(pygame.SCRAP_TEXT).strip() or pygame.scrap.get(pygame.SCRAP_TEXT).strip())
            if content:
                persistent['_mas_player_addition'] = content
            
    modal True
    zorder 92

    use maica_setter_medium_frame(title=renpy.substitute(_("请输入MFocus信息")), ok_action=[Function(apply, edittarget), SetField(persistent ,"selectbool", None), Hide("maica_addition_input")], cancel_action=[SetField(persistent ,"selectbool", None), Hide("maica_addition_input")]):
        hbox:
            input default addition value FieldInputValue(persistent, "_mas_player_addition")
            textbutton _("粘贴"):
                style "mas_button_simple"
                xalign 0.8
                yalign 0.5
                action Function(paste)


screen maica_mspire_input(addition="", edittarget=None):
    python:
        if persistent._mas_player_addition == None:
            persistent._mas_player_addition = ""
        def apply(edittarget):
            addition = persistent._mas_player_addition
            if not persistent._mas_player_addition.strip:
                return
            if addition in persistent.maica_setting_dict["mspire_category"]:
                return
            if edittarget:
                persistent.maica_setting_dict["mspire_category"][persistent.maica_setting_dict["mspire_category"].index(edittarget)] = addition
            else:
                persistent.maica_setting_dict["mspire_category"].append(addition)
            del persistent._mas_player_addition
        def paste(content=None):
            if not content:
                content = (pygame.scrap.get(pygame.SCRAP_TEXT).strip() or pygame.scrap.get(pygame.SCRAP_TEXT).strip())
            if content:
                persistent['_mas_player_addition'] = content

    modal True
    zorder 92

    use maica_setter_medium_frame(title=_("请输入MSpire话题"), ok_action=[Function(apply, edittarget), SetField(persistent, "selectbool", None), Hide("maica_mspire_input")], cancel_action=[SetField(persistent ,"selectbool", None), Hide("maica_mspire_input")]):
        hbox:
            input default addition value FieldInputValue(persistent, "_mas_player_addition")
            textbutton _("粘贴"):
                style "mas_button_simple"
                xalign 0.8
                yalign 0.5
                action Function(paste)

screen maica_location_input(addition="", edittarget=None):
    python:
        if persistent.mas_geolocation == None:
            persistent.mas_geolocation = ""
        if persistent._mas_geolocation == None:
            persistent._mas_geolocation = persistent.mas_geolocation
        def cancel():
            persistent.mas_geolocation = persistent._mas_geolocation
            
    modal True
    zorder 92

    use maica_setter_medium_frame(title=_("请输入地理位置"), ok_action=[SetField(persistent ,"_mas_geolocation", None), Hide("maica_location_input")], cancel_action=[Function(cancel), SetField(persistent ,"_mas_geolocation", None), Hide("maica_location_input")]):
        hbox:
            input default addition value FieldInputValue(persistent, "mas_geolocation")

screen maica_addition_setting():
    $ _tooltip = store._tooltip
    python:
        isinit = False
        if persistent.selectbool == None:
            persistent.selectbool = {}
            isinit = True
        def build_dict():
            persistent.selectbool = {}
            global persistent
            for item in persistent.mas_player_additions:
                persistent.selectbool[item] = False

        if isinit:
            build_dict()
        def delete_seleted():
            global persistent
            persistent.mas_player_additions = [i for i in persistent.mas_player_additions if not persistent.selectbool[i]]

        def selected_one():
            global persistent
            toggled = [k for k, v in iterize(persistent.selectbool) if v]
            if len(toggled) == 1:
                return toggled[0]
            else:
                return False
        
        def selected_count_tf(num=1):
            global persistent
            toggled = [k for k, v in iterize(persistent.selectbool) if v]
            if len(toggled) == num:
                return True
            else:
                return False

        def maica_addition_setting_close():
            global persistent
            persistent.selectbool = None

    modal True
    zorder 92
    on "show" action Function(build_dict)
    use maica_common_outer_frame():
        use maica_common_inner_frame():
            style_prefix "generic_fancy_check"
            for item in persistent.selectbool:
                hbox:
                    textbutton item:
                        action ToggleDict(persistent.selectbool, item)
                    
        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("删除条目"):
                action [SensitiveIf(not selected_count_tf(0)), Function(delete_seleted), Function(build_dict)]

            textbutton _("编辑条目"):
                action [SensitiveIf(selected_count_tf()), Show("maica_addition_input", addition=selected_one(), edittarget=selected_one()), SetField(persistent ,"selectbool", None)]

            textbutton _("添加条目"):
                action [Show("maica_addition_input")]
            
            textbutton _("关闭"):
                action [Function(maica_addition_setting_close), Hide("maica_addition_setting")]


screen maica_mspire_category_setting():
    $ _tooltip = store._tooltip
    python:
        isinit = False
        if persistent.selectbool == None:
            persistent.selectbool = {}
            isinit = True
        def build_dict():
            persistent.selectbool = {}
            global persistent
            for item in persistent.maica_setting_dict["mspire_category"]:
                persistent.selectbool[item] = False

        if isinit:
            build_dict()
        def delete_seleted():
            global persistent
            persistent.maica_setting_dict["mspire_category"] = [i for i in persistent.maica_setting_dict["mspire_category"] if not persistent.selectbool[i]]

        def selected_one():
            global persistent
            toggled = [k for k, v in iterize(persistent.selectbool) if v]
            if len(toggled) == 1:
                return toggled[0]
            else:
                return False

        def selected_count_tf(num=1):
            global persistent
            toggled = [k for k, v in iterize(persistent.selectbool) if v]
            if len(toggled) == num:
                return True
            else:
                return False

        def maica_mspire_setting():
            global persistent
            persistent.selectbool = None

    modal True
    zorder 92
    on "show" action Function(build_dict)
    use maica_common_outer_frame():
        use maica_common_inner_frame():
            style_prefix "generic_fancy_check"
            for item in persistent.selectbool:
                hbox:
                    textbutton item:
                        action ToggleDict(persistent.selectbool, item)
        
        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("删除条目"):
                action [SensitiveIf(not selected_count_tf(0)), Function(delete_seleted), SetField(persistent ,"selectbool", None)]

            textbutton _("编辑条目"):
                action [SensitiveIf(selected_count_tf()), Show("maica_mspire_input", addition=selected_one(), edittarget=selected_one()), SetField(persistent ,"selectbool", None)]

            textbutton _("添加条目"):
                action [Show("maica_mspire_input"),SetField(persistent ,"selectbool", None)]
            
            textbutton _("关闭"):
                action [Function(maica_mspire_setting), Hide("maica_mspire_category_setting")]


screen maica_node_setting():
    $ _tooltip = store._tooltip
    python:
        def set_provider(id):
            persistent.maica_setting_dict["provider_id"] = id

    modal True
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():

            for provider in MaicaProviderManager.servers:
                use maica_l2_subframe():
                    text str(provider.get('id')) + ' | ' + provider.get('name')
                    

                    hbox:
                        text renpy.substitute(_("设备: ")) + provider.get('deviceName', 'Device not provided')
                    hbox:
                        text renpy.substitute(_("当前模型: ")) + provider.get('servingModel', 'No model provided')


                hbox:
                    hbox:
                        style_prefix "generic_fancy_check"
                        textbutton _("使用该节点"):
                            action [
                                Function(set_provider, provider.get('id')),
                                Hide("maica_node_setting")
                            ]
                            selected persistent.maica_setting_dict["provider_id"] == provider.get('id')
                    hbox:
                        style_prefix "maica_check"
                        textbutton renpy.substitute(_("> 打开官网")) + "(" + provider.get('portalPage') + ")":
                            action OpenURL(provider.get('portalPage'))

                    if provider.get("isOfficial", False):
                        hbox:
                            style_prefix "maica_check_nohover"
                            textbutton _(" √ MAICA 官方服务器")
                        
        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("刷新节点列表"):
                action Function(store.maica.maica.MaicaProviderManager.get_provider)

            textbutton _("关闭"):
                action Hide("maica_node_setting")
            
            textbutton _("测试当前节点可用性"):
                action Function(store.maica.maica.accessable)
                        
screen maica_mspire_setting():
    $ _tooltip = store._tooltip

    modal True
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():

            style_prefix "generic_fancy_check"
            textbutton "percise_page":
                action SetDict(persistent.maica_setting_dict, "mspire_search_type", "percise_page")
            text _("仅选取与搜索关键词最接近的一个页面, 此时采样广度不生效. 此种类条目不执行递归查找, 响应较快.\n"):
                style "small_expl_hw"
                size 15
            textbutton "fuzzy_page":
                action SetDict(persistent.maica_setting_dict, "mspire_search_type", "fuzzy_page")
            text _("根据关键词搜索多个页面, 从中随机抽取一个页面. 此种类条目不执行递归查找, 响应较快.\n"):
                style "small_expl_hw"
                size 15
            textbutton "in_percise_category":
                action SetDict(persistent.maica_setting_dict, "mspire_search_type", "in_percise_category")
            text _("先仅选取与搜索关键词最接近的一个分类, 再从其中递归地随机抽取分类或页面, 直至最终抽取到一个页面. 此种类条目响应较慢.\n"):
                style "small_expl_hw"
                size 15
            textbutton "in_fuzzy_category":
                action SetDict(persistent.maica_setting_dict, "mspire_search_type", "in_fuzzy_category")
            text _("根据关键词搜索多个分类, 再从其中递归地随机抽取分类或页面, 直至最终抽取到一个页面. 此种类条目响应较慢.\n"):
                style "small_expl_hw"
                size 15
            textbutton "in_fuzzy_all":
                action SetDict(persistent.maica_setting_dict, "mspire_search_type", "in_fuzzy_all")
            text _("根据关键词直接开始递归地抽取分类或页面, 直至最终抽取到一个页面. 此种类条目响应较慢.\n"):
                style "small_expl_hw"
                size 15

        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("关闭"):
                action Hide("maica_mspire_setting")
            
                # textbutton _("当前方式: [persistent.maica_setting_dict.get('mspire_search_type', 'None')]")


screen maica_triggers():
    $ _tooltip = store._tooltip
    python:
        maica_triggers = store.maica.maica.mtrigger_manager

    modal True
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():
    
            style_prefix "generic_fancy_check"
            text _("MTrigger空间使用情况: ")

            if maica_triggers.get_length(0) > maica_triggers.MAX_LENGTH_REQUEST * 0.75:
                text "request: " + str(maica_triggers.get_length(0)) + " / " + str(maica_triggers.MAX_LENGTH_REQUEST):
                    color "#FF0000"
            else:
                text "request: " + str(maica_triggers.get_length(0)) + " / " + str(maica_triggers.MAX_LENGTH_REQUEST)

            if maica_triggers.get_length(1) > maica_triggers.MAX_LENGTH_TABLE * 0.9:
                text "table: " + str(maica_triggers.get_length(1)) + " / " + str(maica_triggers.MAX_LENGTH_TABLE):
                    color "#FF0000"
            else:
                text "table: " + str(maica_triggers.get_length(1)) + " / " + str(maica_triggers.MAX_LENGTH_TABLE)

            if maica_triggers.get_length(0) > maica_triggers.MAX_LENGTH_REQUEST * 0.75 or maica_triggers.get_length(1) > maica_triggers.MAX_LENGTH_TABLE * 0.9:
                text _("> 注意: 当空间不足时将自动关闭部分MTrigger!"):
                    color "#ff0000"
                    size 15

            for trigger in maica_triggers.triggers:
                use maica_l2_subframe():
                    label trigger.name
                    if not maica_triggers.trigger_status(trigger.name) or not trigger.condition():
                        hbox:
                            text _("空间占用: -"):
                                size 15
                    elif trigger.method == 0:
                        hbox:
                            text _("空间占用: request"):
                                size 15
                            text str(len(trigger)):
                                size 15
                    elif trigger.method == 1:
                        hbox:
                            text _("空间占用: table"):
                                size 15
                            text str(len(trigger)):
                                size 15

                    hbox:
                        if hasattr(trigger, 'web_musicplayer_installed'):
                            text _("内置 | 更换背景音乐 "):
                                size 15
                            hbox:
                                style_prefix "small_expl_hw"
                                text _("* 支持 "):
                                    size 15
                                textbutton "{u}Netease Music{/u}":
                                    action OpenURL("https://github.com/MAS-Submod-MoyuTeam/NeteaseInMas")
                                text _(" 和 "):
                                    size 15
                                textbutton "{u}Youtube Music{/u}":
                                    action OpenURL("https://github.com/Booplicate/MAS-Submods-YouTubeMusic")
                                text _(" 子模组"):
                                    size 15

                        else:
                            text trigger.description:
                                size 15
                    
                    
                    
                    hbox:
                        if trigger.condition():
                            if maica_triggers.trigger_status(trigger.name):
                                textbutton _("已启用"):
                                    action Function(maica_triggers.disable_trigger, trigger.name)
                                    selected maica_triggers.trigger_status(trigger.name)
                            else:
                                textbutton _("已禁用"):
                                    action Function(maica_triggers.enable_trigger, trigger.name)
                                    selected maica_triggers.trigger_status(trigger.name)
                            
                        else:
                            if maica_triggers.trigger_status(trigger.name):
                                textbutton _("当前不满足触发条件"):
                                    style "generic_fancy_check_button_disabled"
                                    action Function(maica_triggers.disable_trigger, trigger.name)
                                    selected maica_triggers.trigger_status(trigger.name)
                            else:
                                textbutton _("当前不满足触发条件"):
                                    style "generic_fancy_check_button_disabled"
                                    action Function(maica_triggers.enable_trigger, trigger.name)
                                    selected maica_triggers.trigger_status(trigger.name)
        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("关闭"):
                action Hide("maica_triggers")

screen maica_mpostals():
    python:
        import time
        maica_triggers = store.maica.maica.mtrigger_manager
        preview_len = 200

        def _delect_portal(title):
            for item in persistent._maica_send_or_received_mpostals:
                if title == item["raw_title"]:
                    persistent._maica_send_or_received_mpostals.remove(item)
                    break

    $ _tooltip = store._tooltip

    modal True
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():
    
            style_prefix "maica_check"
            hbox:
                text ""
            for postal in persistent._maica_send_or_received_mpostals:
                use maica_l2_subframe():
                    label postal["raw_title"]:
                        style "maica_check_nohover_label"
                    text renpy.substitute(_("信件状态: ")) + postal["responsed_status"]:
                        xalign 0.0
                        style "small_link"
                    text renpy.substitute(_("寄信时间: ")) + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(postal["time"].split(".")[0]))):
                        xalign 0.0
                        style "small_link"
                    text renpy.substitute(_("\n[player]: \n")) + postal["raw_content"][:preview_len].replace("\n", "") + ("..." if len(postal["raw_content"]) > preview_len else  ""):
                        xalign 0.0
                        style "small_expl_hw"
                    if postal["responsed_content"] != "":
                        text renpy.substitute(_("[m_name]: \n")) + postal["responsed_content"][:preview_len].replace("\n", "")  + ("..." if len(postal["responsed_content"]) > preview_len else  "") + "\n":
                            xalign 0.0
                            style "small_expl_hw"
                    hbox:
                        textbutton _("阅读[player]写的信"):
                            action [
                                    Hide("maica_mpostals"),
                                    Hide("maica_setting"),
                                    Function(store.maica_apply_setting),
                                    Function(renpy.call, "maica_mpostal_show_backtoscreen", content = postal["raw_content"])
                            ]
                        if postal["responsed_content"] != "":
                            textbutton _("阅读[m_name]的回信"):
                                action [
                                        Hide("maica_mpostals"),
                                        Hide("maica_setting"),
                                        Function(store.maica_apply_setting),
                                        Function(renpy.call, "maica_mpostal_show_backtoscreen", content = postal["responsed_content"])
                                ]
                        
                        if postal["responsed_status"] in ("fatal"):
                            textbutton _("重新寄信"):
                                action SetDict(postal, "responsed_status", "delaying")
                        hbox:
                            textbutton _("删除"):
                                action Function(_delect_portal, postal["raw_title"])
                        
        hbox:
            xpos 10
            style_prefix "confirm"
            textbutton _("关闭"):
                action Hide("maica_mpostals")

screen maica_support():

    modal True
    zorder 92

    use maica_setter_medium_frame(title=_("向 MAICA 捐赠"), ok_action=Hide("maica_support")):
        hbox:
            text _("首先很感谢你有心捐赠.\n我们收到的捐赠基本上不可能回本, 但你不必有任何压力.")
        hbox:
            style_prefix "maica_check"
            text _("请注意, 向MAICA捐赠不会提供任何特权, 除了论坛捐赠页名单和捐赠徽章."):
                size 15
        hbox:
            xalign 0.5
            if config.language == 'chinese':
                imagebutton:
                    idle "mod_assets/maica_img/aifadian.png"
                    insensitive "mod_assets/maica_img/aifadian.png"
                    hover "mod_assets/maica_img/aifadian.png"
                    selected_idle "mod_assets/maica_img/aifadian.png"
                    selected_hover "mod_assets/maica_img/aifadian.png"
                    action OpenURL("https://forum.monika.love/iframe/redir_donation.php?lang=zh")
            else:
                imagebutton:
                    idle "mod_assets/maica_img/unifans.png"
                    insensitive "mod_assets/maica_img/unifans.png"
                    hover "mod_assets/maica_img/unifans.png"
                    selected_idle "mod_assets/maica_img/unifans.png"
                    selected_hover "mod_assets/maica_img/unifans.png"
                    action OpenURL("https://forum.monika.love/iframe/redir_donation.php?lang=en")

screen maica_workload_stat_lite():
    python:
        onliners = store.maica.maica.workload_raw.get("onliners")
        ai = store.maica.maica
        data = ai.get_workload_lite()
        store.update_interval = 15

        @store.workload_throttle
        def check_and_update():
            store.maica.maica.update_workload()
    
    zorder 100
    fixed:
        frame:
            xsize 619
            xoffset 5 yoffset 450
            background "mod_assets/console/cn_frame_stats.png"
            has vbox
            hbox:
                text renpy.substitute(_("当前在线人数: ")) + str(onliners):
                    size 15
                hbox:
                    text "  ":
                        size 15
                    text renpy.substitute(_("下次更新数据")):
                        size 15
                    text store.maica.progress_bar(((store.workload_throttle.remain / store.update_interval)) * 100, bar_length = 10, total=store.update_interval, unit="s"):
                        size 15
                        font maica_confont
                    timer 1.0 repeat True action Function(check_and_update)

            hbox:
                text "VRAM " + (maica.progress_bar(data["total_inuse_vmem"]  * 100 / data["total_vmem"], total=int(data["total_vmem"]), unit="MiB", bar_length = 30) if data["total_vmem"] != 0 else "No memory information"):
                    size 15
                    font maica_confont
            hbox:
                text "UTIL " + maica.progress_bar(data["avg_usage"], total=int(data["max_tflops"]), unit="TFlops", bar_length = 30):
                    size 15
                    font maica_confont




screen maica_workload_stat():
    $ _tooltip = store._tooltip
    python:
        stat = {k: v for k, v in iterize(store.maica.maica.workload_raw) if k != "onliners"}
        onliners = store.maica.maica.workload_raw.get("onliners")
    python:
        store.update_interval = 15

        @store.workload_throttle
        def check_and_update():
            store.maica.maica.update_workload()

    modal True
    zorder 90
    
    style_prefix "check"

    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            style_prefix "maica_default_small"
            xsize 942
            spacing 5

            text renpy.substitute(_("当前在线人数: ")) + str(onliners)

            for server in stat:

                use divider_small(server)

                for card in stat[server]:
                    hbox:
                        text stat[server][card]["name"]:
                            size 15
                        text store.maica.progress_bar(stat[server][card]["mean_utilization"], total=int(stat[server][card]["tflops"]), unit="TFlops"):
                            size 10
                            font maica_confont

                        text "VRAM: " + str(stat[server][card]["mean_memory"]) + " / " + str(stat[server][card]["vram"]):
                            size 10
                        text renpy.substitute(_("平均功耗: ")) + str(stat[server][card]["mean_consumption"]) + "W":
                            size 10
                text ""

            hbox:
                text renpy.substitute(_("下次更新数据")):
                    size 15
                text store.maica.progress_bar(((store.workload_throttle.remain / store.update_interval)) * 100, bar_length = 78, total=store.update_interval, unit="s"):
                    size 15
                    font maica_confont
                timer 1.0 repeat True action Function(check_and_update)

screen maica_select_console_font():
    modal True
    zorder 92

    use maica_setter_small_frame(ok_action=Hide("maica_select_console_font")):
        style_prefix "generic_fancy_check"
        hbox:
            textbutton _("SarasaMonoTC | 思源黑体等宽"):
                action SetDict(persistent.maica_setting_dict, "console_font", store.maica_confont)
        hbox:
            textbutton _("mplus-1mn | 默认等宽字体"):
                action SetDict(persistent.maica_setting_dict, "console_font", store.mas_ui.MONO_FONT)

screen maica_select_log_level(log = "log_level"):
    modal True
    zorder 92
    python:
        import logging
        log_levels = [
            (logging.NOTSET, _("NOTSET")),
            (logging.DEBUG, _("DEBUG")),
            (logging.INFO, _("INFO")),
            (logging.WARNING, _("WARNING")),
            (logging.ERROR, _("ERROR")),
            (logging.CRITICAL, _("CRITICAL"))
        ]

    use maica_setter_small_frame(ok_action=Hide("maica_select_log_level")):
        style_prefix "generic_fancy_check"
        for level, name in log_levels:
            hbox:
                textbutton "{} | {}".format(level, name):
                    action SetDict(persistent.maica_setting_dict, log, level)
                    selected level == persistent.maica_setting_dict[log]

screen maica_statics():
    $ _tooltip = store._tooltip

    modal True
    zorder 90
    
    style_prefix "check"

    frame:
        xalign 0.5
        yalign 0.5
        vbox:
            style_prefix "maica_default_small"
            xsize 942
            spacing 5
            hbox:
                text _("累计对话轮次: [store.maica.maica.stat.get('message_count')]"):
                    size 20
            hbox:
                text _("累计MSpire轮次: [store.maica.maica.stat.get('mspire_count')]"):
                    size 20
            hbox:
                text _("累计收到Token: [store.maica.maica.stat.get('received_token')]"):
                    size 20
            hbox:
                text _("每个会话累计Token: [store.maica.maica.stat.get('received_token_by_session')]"):
                    size 20
            hbox:
                text _("累计发信数: [store.maica.maica.stat.get('mpostal_count')]"):
                    size 20
            hbox:
                $ user_disp = store.maica.maica.user_acc or renpy.substitute(_("未登录"))
                text _("当前用户: [user_disp]"):
                    size 20

            hbox:
                xpos 10
                style_prefix "confirm"
                textbutton _("重置统计数据"):
                    action Function(store.maica.maica.reset_stat)