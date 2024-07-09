
    #store.mas_submod_utils.Submod(
    #    author=submod_author,
    #    name=submod_name,
    #    description=submod_description,
    #    version=submod_version
    #)

# 这里是为了使用游戏内更新插件,教学请移步'莫妮卡的子模组教学'
# 这里就把这段代码全部注释了
#init -989 python:
#    if store.mas_submod_utils.isSubmodInstalled("Submod Updater Plugin"):
#        store.sup_utils.SubmodUpdater(
#            submod="Custom Room Furnished Spaceroom V3",
#            user_name="tw4449",
#            repository_name="Custom-Room-Furnished-Spaceroom-V3",
#            update_dir="",
#            attachment_id=None
#        )

# 白天
image heaven_forest_day = "mod_assets/location/heaven_forest/heaven_forest.jpg"
image heaven_forest_rain = "mod_assets/location/heaven_forest/heaven_forest.jpg"
image heaven_forest_overcast ="mod_assets/location/heaven_forest/heaven_forest.jpg"
image heaven_forest_snow = "mod_assets/location/heaven_forest/heaven_forest.jpg"

# 晚上
image heaven_forest_night= "mod_assets/location/heaven_forest/heaven_forest.jpg"
image heaven_forest_rain_night = "mod_assets/location/heaven_forest/heaven_forest.jpg"
image heaven_forest_overcast_night = "mod_assets/location/heaven_forest/heaven_forest.jpg"
image heaven_forest_snow_night = "mod_assets/location/heaven_forest/heaven_forest.jpg"

# 傍晚
image heaven_forest_ss = "mod_assets/location/heaven_forest/heaven_forest.jpg"
image heaven_forest_rain_ss = "mod_assets/location/heaven_forest/heaven_forest.jpg"
image heaven_forest_overcast_ss ="mod_assets/location/heaven_forest/heaven_forest.jpg"
image heaven_forest_snow_ss = "mod_assets/location/heaven_forest/heaven_forest.jpg"

### 这里疑似是为特殊日期（生日,万圣节等)处理装饰的地方,如果不需要请注释
#init 501 python:
#    MASImageTagDecoDefinition.register_img(
#        "mas_o31_ceiling_lights",
#        submod_background_Furnished_spaceroom3.background_id,
#        MASAdvancedDecoFrame(zorder=5)
#    )

    #MASImageTagDecoDefinition.register_img(
#        "mas_o31_ceiling_deco",
#        submod_background_Furnished_spaceroom3.background_id,
#        MASAdvancedDecoFrame(zorder=6)
#    )
#
#    MASImageTagDecoDefinition.register_img(
#        "mas_o31_window_ghost",
#        submod_background_Furnished_spaceroom3.background_id,
#        MASAdvancedDecoFrame(zorder=4)
#    )

#    MASImageTagDecoDefinition.register_img(
#        "mas_o31_vignette",
#        submod_background_Furnished_spaceroom3.background_id,
#        MASAdvancedDecoFrame(zorder=21) #21 Zorder 缩放（到底是缩放还是图层我不太明白）这会在所有CG的上层[原注释]
#    )
### 如果你没有装饰,注释到这里.

init -1 python:
    heaven_forest = MASFilterableBackground(
        "heaven_forest",
        "天堂森林",
        MASFilterWeatherMap(
            #白天
            day=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "heaven_forest_day",
                store.mas_weather.PRECIP_TYPE_RAIN: "heaven_forest_rain",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "heaven_forest_overcast",
                store.mas_weather.PRECIP_TYPE_SNOW: "heaven_forest_snow",
            }),
            #晚上
            night=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "heaven_forest_night",
                store.mas_weather.PRECIP_TYPE_RAIN: "heaven_forest_rain_night",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "heaven_forest_overcast_night",
                store.mas_weather.PRECIP_TYPE_SNOW: "heaven_forest_snow_night",
            }),
            #傍晚
            sunset=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "heaven_forest_ss",
                store.mas_weather.PRECIP_TYPE_RAIN: "heaven_forest_rain_ss",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "heaven_forest_overcast_ss",
                store.mas_weather.PRECIP_TYPE_SNOW: "heaven_forest_snow_ss",
            }),
        ),

# 说明那些图片应该在什么时候显示,如果没有特别要求,保持原样就好.
        MASBackgroundFilterManager(
            MASBackgroundFilterChunk(
                False,
                None,
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_NIGHT,
                    60
                )
            ),
            MASBackgroundFilterChunk(
                True,
                None,
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_SUNSET,
                    60,
                    30*60,
                    10,
                ),
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_DAY,
                    60
                ),
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_SUNSET,
                    60,
                    30*60,
                    10,
                ),
            ),
            MASBackgroundFilterChunk(
                False,
                None,
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_NIGHT,
                    60
                )
            )
        ),
        ##############################################
        # 房间细节 True=是,False=否
        ##############################################

        disable_progressive=True,    #是否禁用天气变化
        hide_masks=True,             #是否禁用天气动画
        hide_calendar=True,          #是否隐藏日历
        unlocked=False,                #是否解锁
        entry_pp=store.mas_background._entry,   #没必要改
        exit_pp=store.mas_background._exit,     #↑
        ex_props={"skip_outro": None}           #↑
    )


init -2 python in mas_background:
    def _entry(_old, **kwargs):
        """
        进入这个房间执行的代码
        """
        if kwargs.get("startup"):
            pass

        else:
            store.mas_o31HideVisuals()
            store.mas_d25HideVisuals()

        ##############################################
        # 桌椅贴图 没有就别改
        ##############################################

        #更改桌椅贴图 monika/t/
        store.monika_chr.tablechair.table = "def"
        #table-def.png
        store.monika_chr.tablechair.chair = "def"
        #chair-def.png
        #如果你有自己的贴图，命名格式为table-<图片id>.png 图片id与要填在上面的一样
        #chair同理

        if store.seen_event("mas_monika_islands"):
            store.mas_unlockEVL("mas_monika_islands", "EVE")

    def _exit(_new, **kwargs):
        """
        离开这个房间执行的代码 不需要改
        """
        #O31
        if store.persistent._mas_o31_in_o31_mode:
            store.mas_o31ShowVisuals()

        #D25
        elif store.persistent._mas_d25_deco_active:
            store.mas_d25ShowVisuals()

        #确保锁定小岛对话.
        store.mas_lockEVL("mas_monika_islands", "EVE")

        #这里就别改了
        store.monika_chr.tablechair.table = "def"
        store.monika_chr.tablechair.chair = "def"




