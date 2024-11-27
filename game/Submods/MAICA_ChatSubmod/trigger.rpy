
init 999 python in maica:
    from maica_mtrigger import *
    import store
    class AffTrigger(MTriggerBase):
        def __init__(self, template, name, callback):
            super(AffTrigger, self).__init__(template, name, callback=callback, description = _("内置 | 调整好感, 范围为单次-1~3"))
        
        def triggered(self, data):
            return self.callback(data.get("affection", 0.1))

    def aff_callback(affection):
        #from math import ceil
        affection = float(affection)
        maica.send_to_outside_func("<mtrigger> aff_callback called")
        if affection < 0:
            store.mas_loseAffection(1, -affection)
        elif affection > 0:
            store.mas_gainAffection(1, affection)

    aff_trigger = AffTrigger(common_affection_template, "alter_affection", callback=aff_callback)
    maica.mtrigger_manager.add_trigger(aff_trigger)

#################################################################################

    class ClothesTrigger(MTriggerBase):
        def __init__(self, template, name):
            self.clothes_data = {store.mas_selspr.CLOTH_SEL_MAP[key].display_name:key for key in store.mas_selspr.CLOTH_SEL_MAP if self.outfit_has_and_unlocked(key)}
            self.clothes_data["玩家挑选"] = "mas_pick_a_clothes"
            self.clothes_data[False] = "mas_pick_a_clothes"
            super(ClothesTrigger, self).__init__(template, name, description=_("内置 | 更换衣服"),callback=self.clothes_callback, 
                exprop=MTriggerExprop(
                    item_name_zh = "更换游戏内服装",
                    item_name_en = "change in-game outfit",
                    item_list = self.clothes_data.keys(),
                    curr_value = store.mas_selspr.CLOTH_SEL_MAP[store.monika_chr.clothes.name].display_name,
                ),
                action = MTriggerAction.post,
            )
        def outfit_has_and_unlocked(self, outfit_name):
            """
            Returns True if we have the outfit and it's unlocked
            """
            return outfit_name in store.mas_selspr.CLOTH_SEL_MAP and store.mas_selspr.CLOTH_SEL_MAP[outfit_name].unlocked

        def triggered(self, data):
            clothes = data.get("selection", None)
            if clothes is not None:
                self.callback(clothes)

        def clothes_callback(self, clothes):
            if not clothes in self.clothes_data:
                maica.send_to_outside_func("<mtrigger> {} is not a vaild outfit".format(clothes))
                store.mas_submod_utils.submod_log.error("maica: {} is not a valid outfit".format(clothes))
                return
            return store.renpy.call("mtrigger_change_clothes", self.clothes_data[clothes])

    clothes_trigger = ClothesTrigger(common_switch_template, "clothes")
    maica.mtrigger_manager.add_trigger(clothes_trigger)

#################################################################################

    unlocked_games_dict = {
        ev.prompt: ev.eventlabel
        for ev in store.mas_games.game_db.values()
        if store.mas_isGameUnlocked(ev.prompt)
    }
    
    unlocked_games_dict["玩家自行选择"] = "mas_pick_a_game"
    unlocked_games_dict[False] = "mas_pick_a_game"
    unlocked_games_dict["Pong"] = "game_pong"
    if "NOU" in unlocked_games_dict:
        unlocked_games_dict["UNO"] = unlocked_games_dict["NOU"]
    if store.mas_isGameUnlocked("Hangman") or store.mas_isGameUnlocked("上吊小人"):
        unlocked_games_dict["Hangman"] = "game_hangman"
    def minigame_callback(item):
        
        if not item in unlocked_games_dict:
            maica.send_to_outside_func("<mtrigger> {} is not a vaild minigame".format(item))
            store.mas_submod_utils.submod_log.error("maica: {} is not a valid minigame".format(item))
            return
        game_label = unlocked_games_dict[item]
        store.renpy.call("mttrigger_minigame", game_label)
    
    minigame_trigger = MTriggerBase(common_switch_template, "minigame", callback=minigame_callback,
        exprop=MTriggerExprop(
            item_name_zh="小游戏",
            item_name_en="minigame",
            item_list=unlocked_games_dict.keys(),
        ),
        description = _("内置 | 拉起小游戏")
    )
    maica.mtrigger_manager.add_trigger(minigame_trigger)
    

#################################################################################

    def mtrigger_kiss_condition():
        return store.mas_shouldKiss(1)

    def mtrigger_kiss_callback(arg):
        store.renpy.call("mtrigger_kiss")

    kiss_trigger = MTriggerBase(customize_template, "kiss", "亲吻玩家", "kiss player", condition=mtrigger_kiss_condition, callback=mtrigger_kiss_callback,
        description = _("内置 | 调用亲吻事件"))
    maica.mtrigger_manager.add_trigger(kiss_trigger)

#################################################################################

    def mtrigger_leave_callback(arg):
        maica.send_to_outside_func("<mtrigger> mtrigger_leave_callback called")
        store.renpy.call("mtrigger_leave")
    leave_trigger = MTriggerBase(customize_template, "leave", "帮助玩家离开游戏", "help player quit game", callback=mtrigger_leave_callback, description=_("内置 | 关闭游戏"))
    maica.mtrigger_manager.add_trigger(leave_trigger)

#################################################################################

    def mtrigger_idle_callback(arg):
        maica.send_to_outside_func("<mtrigger> mtrigger_leave_callback called")
        store.renpy.call("mtrigger_leave")
    idle_trigger = MTriggerBase(customize_template, "idle", "帮助玩家短暂休息", "help player afk short time", callback=mtrigger_idle_callback, description=_("内置 | 暂离"))
    maica.mtrigger_manager.add_trigger(idle_trigger)

#################################################################################

    class WeatherTrigger(MTriggerBase):
        def __init__(self):
            self.weathers = self.get_weather_dict()
            self.weathers_list = self.get_weather_list()
            super(WeatherTrigger, self).__init__(
                common_switch_template,
                "weather",
                exprop=MTriggerExprop(
                    item_name_zh="游戏内天气",
                    item_name_en="in-game weather",
                    item_list=self.weathers_list,
                    curr_value=store.mas_current_weather.prompt
                ),
                callback = self.callback,
                description = _("内置 | 更换天气 {size=-5}* 在天堂树林内不启用"),
                condition = self.condition
            )

        def condition(self):
            current = store.mas_getCurrentBackgroundId()
            return store.mas_isMoniAff(higher=True) and not current in("heaven_forest_d", "heaven_forest")
            
        def build(self):
            self.weathers = self.get_weather_dict()
            self.weathers_list = self.get_weather_list()
            return super(WeatherTrigger, self).build()

        def get_weather_list(self):
            return self.weathers.keys()

        def get_weather_dict(self):
            import store.mas_weather as mas_weather

            # Default weather at the top
            weathers = {store.mas_weather_def.prompt: store.mas_weather_def}

            # Build and sort other weather list
            other_weathers = {
                mw_obj.prompt: mw_obj
                for mw_id, mw_obj in mas_weather.WEATHER_MAP.items()
                if mw_id != "def" and mw_obj.unlocked
            }

            # Sort by prompt and merge with default weather
            sorted_weathers = dict(sorted(other_weathers.items()))
            weathers.update(sorted_weathers)

            return weathers

        def callback(self, selection):
            selection = u"\u6674\u5929" if selection == "Clear" and u"\u6674\u5929" in self.weathers else selection
            if not selection in self.weathers:
                store.mas_submod_utils.submod_log.error("maica: {} is not a valid weather!".format(selection))
                maica.send_to_outside_func("<mtrigger> {} is not a valid weather!".format(selection))
                return
            weather = self.weathers[selection]
            store.renpy.call("mas_change_weather", weather, by_user=True, set_persistent=True)
    weather_trigger = WeatherTrigger()
    maica.mtrigger_manager.add_trigger(weather_trigger)

#################################################################################

    def mtrigger_location_condition():
        return store.mas_isMoniEnamored(True)

    def mtrigger_location_callback(arg):
        store.renpy.call("mtrigger_location")

    location_trigger = MTriggerBase(customize_template, "location", "切换游戏内场景", "change in-game location", condition=mtrigger_location_condition, callback=mtrigger_location_callback,
        description = _("内置 | 调用切换房间"))
    maica.mtrigger_manager.add_trigger(location_trigger)

#################################################################################

    def mtrigger_backup_condition():
        return store.mas_submod_utils.isSubmodInstalled("Extra Plus")

    def mtrigger_backup_callback(arg):
        store.renpy.call("mas_backup")

    backup_trigger = MTriggerBase(customize_template, "backup", "备份存档", "backup savefile", condition=mtrigger_backup_condition, callback=mtrigger_backup_callback,
        description = _("内置 | 备份存档 {size=-5}* 需要 Extra Plus 子模组"))
    maica.mtrigger_manager.add_trigger(backup_trigger)

#################################################################################

    def mtrigger_hold_condition():
        return store.renpy.seen_label("monika_holdme_prep")

    def mtrigger_hold_callback(arg):
        store.renpy.call("mtrigger_hold")

    hold_trigger = MTriggerBase(customize_template, "hold", "拥抱玩家", "hold player", condition=mtrigger_hold_condition, callback=mtrigger_hold_callback,
        description = _("内置 | 拥抱"))
    maica.mtrigger_manager.add_trigger(hold_trigger)

#################################################################################

        






