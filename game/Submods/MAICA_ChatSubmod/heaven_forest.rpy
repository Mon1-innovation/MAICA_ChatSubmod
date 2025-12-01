
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
define use_amim_background = persistent.maica_setting_dict.get("use_anim_background", True) if persistent.maica_setting_dict else True
# 白天
image heaven_forest_day = Movie(play="mod_assets/location/heaven_forest/heaven_classroom.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom.jpg"
image heaven_forest_rain = Movie(play="mod_assets/location/heaven_forest/heaven_classroom.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom.jpg"
image heaven_forest_overcast = Movie(play="mod_assets/location/heaven_forest/heaven_classroom.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom.jpg"
image heaven_forest_snow = Movie(play="mod_assets/location/heaven_forest/heaven_classroom.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom.jpg"

# 晚上
image heaven_forest_night = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_n.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_n.jpg"
image heaven_forest_rain_night = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_n.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_n.jpg"
image heaven_forest_overcast_night = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_n.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_n.jpg"
image heaven_forest_snow_night = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_n.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_n.jpg"

# 傍晚
image heaven_forest_ss = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_ss.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_ss.jpg"
image heaven_forest_rain_ss = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_ss.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_ss.jpg"
image heaven_forest_overcast_ss = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_ss.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_ss.jpg"
image heaven_forest_snow_ss = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_ss.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_ss.jpg"

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
    def hf_show(_old, **kwargs):
        pass
        #$ behind_bg = MAS_BACKGROUND_Z - 1
        #show heaven_forest_day as sp_mas_backbed zorder behind_bg
        #renpy.show("heaven_forest_day", as_="sp_mas_backbed", zorder=MAS_BACKGROUND_Z - 1)
    def hf_hide(_new, **kwargs):
        pass
        #renpy.hide("sp_mas_backbed")
        #f store.mas_inEVL("maica_hf_hide_bg"):
        #   store.pushEvent("maica_hf_hide_bg")

    heaven_forest = MASFilterableBackground(
        # ID
        "heaven_forest",
        "heaven_forest",

        # mapping of filters to MASWeatherMaps
        MASFilterWeatherMap(
            day=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "monika_day_room",
                store.mas_weather.PRECIP_TYPE_RAIN: "monika_rain_room",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "monika_rain_room",
                store.mas_weather.PRECIP_TYPE_SNOW: "monika_snow_room_day",
            }),
            night=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "monika_room",
                store.mas_weather.PRECIP_TYPE_SNOW: "monika_snow_room_night",
            }),
            sunset=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "monika_ss_room",
                store.mas_weather.PRECIP_TYPE_RAIN: "monika_rain_room_ss",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "monika_rain_room_ss",
                store.mas_weather.PRECIP_TYPE_SNOW: "monika_snow_room_ss",
            }),
        ),

        # filter manager
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

        unlocked=True,
        entry_pp=store.hf_hide,
        exit_pp=store.hf_show,
    )

