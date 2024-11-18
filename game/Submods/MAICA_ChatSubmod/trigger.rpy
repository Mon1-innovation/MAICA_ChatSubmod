
init 999 python in maica:
    from maica_mtrigger import *
    import store
    class AffTrigger(MTriggerBase):
        def __init__(self, template, name, callback):
            super(AffTrigger, self).__init__(template, name, "triggered aff", "triggered aff", callback=callback, description = _("内置 | 调整好感, 范围为单次-1~3"), exprop=MTriggerExprop(value_limits=[-1, 3]))
        
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
            self.clothes_data = {key: store.mas_selspr.CLOTH_SEL_MAP[key].name for key in store.mas_selspr.CLOTH_SEL_MAP if self.outfit_has_and_unlocked(key)}
            super(ClothesTrigger, self).__init__(template, name, "衣服", "clothes", description=_("内置 | 更换衣服"),callback=self.clothes_callback, 
                exprop=MTriggerExprop(
                    item_name_zh = "衣服",
                    item_name_en = "outfit",
                    item_list = self.clothes_data.keys(),
                    curr_value = store.monika_chr.clothes.name,
                ),
                action = MTriggerAction.post
            )
        def outfit_has_and_unlocked(self, outfit_name):
            """
            Returns True if we have the outfit and it's unlocked
            """
            return outfit_name in store.mas_selspr.CLOTH_SEL_MAP and store.mas_selspr.CLOTH_SEL_MAP[outfit_name].unlocked

        def triggered(self, data):
            clothes = data.get("selection", None)
            if clothes is not None:
                self.callback(self.clothes_data[clothes])

        def clothes_callback(self, clothes):
            maica.send_to_outside_func("<mtrigger> clothes_callback called")
            return store.renpy.call("mtrigger_change_clothes", clothes)
            outfit_name = self.clothes_data[clothes]
            outfit_to_wear = store.mas_sprites.get_sprite(
                store.mas_sprites.SP_CLOTHES,
                outfit_name
            )
            if outfit_to_wear is not None and store.mas_SELisUnlocked(outfit_to_wear):
                pass
                #store.monika_chr.change_clothes(outfit_to_wear, by_user=True, outfit_mode=True)

    clothes_trigger = ClothesTrigger(common_switch_template, "clothes")
    maica.mtrigger_manager.add_trigger(clothes_trigger)

#################################################################################

    unlocked_games_dict = {
        ev.prompt: ev.eventlabel
        for ev in store.mas_games.game_db.values()
        if store.mas_isGameUnlocked(ev.prompt)
    }

    def minigame_callback(item):
        maica.send_to_outside_func("<mtrigger> minigame_callback called")
        game_label = unlocked_games_dict[item]
        store.renpy.call(game_label)
    
    minigame_trigger = MTriggerBase(common_switch_template, "minigame", "玩小游戏", "play minigame", callback=minigame_callback,
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

    def mtrigger_kiss_callback():
        store.renpy.call("mtrigger_kiss")

    kiss_trigger = MTriggerBase(customize_template, "kiss", "亲吻", "kiss", condition=mtrigger_kiss_condition, callback=mtrigger_kiss_callback,
        description = _("内置 | 调用亲吻事件"))
    maica.mtrigger_manager.add_trigger(kiss_trigger)

#################################################################################

    def mtrigger_leave_callback():
        store.renpy.call("mtrigger_leave")
    leave_trigger = MTriggerBase(customize_template, "leave", callback=store.renpy.mtrigger_leave_callback, description=_("内置 | 关闭游戏"))
    maica.mtrigger_manager.add_trigger(leave_trigger)

#################################################################################

    class WeatherTrigger(MTriggerBase):
        def __init__(self, template, name):
            self.weathers = self.get_weather_dict()
            super(WeatherTrigger, self).__init__(
                common_switch_template,
                "weather",
                exprop=MTriggerExprop(
                    item_name_zh="天气",
                    item_name_en="weather",
                    item_list=self.weathers,
                    curr_value=store.mas_current_weather
                )
                callback = self.callback,
                description = _("内置 | 更换天气"),
                condition = self.condition
            )

        def condition(self):
            return mas_isMoniAff(higher=True)
            
        def build(self):
            self.weathers = self.get_weather_dict()
            return super(WeatherTrigger, self).build()

        def get_weather_list(self):
            return self.weathers.keys()

        def get_weather_dict(self):
            import store.mas_weather as mas_weather

            # Default weather at the top
            weathers = {mas_weather_def.prompt: mas_weather_def}

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
            weather = self.weathers[selection]
            store.renpy.call("mas_change_weather", weather, by_user=True, set_persistent=True)
    weather_trigger = WeatherTrigger()
    maica.mtrigger_manager.add_trigger(weather_trigger)

#################################################################################




        






