#======================================================================
#请先修改本文件的文件名（英文加数字·但不能以数字开头）
#v2版本相比v1版本,简化了一些操作
#你只需要创建好这里的文件夹,然后修改下面的东西就好了
#你需要修改的东西（大概行数）：
#11行 基本配置 房间细节
#233行 桌椅贴图
#277行 选择对话
#======================================================================


init -990 python:
    ##############################################
    # 基本配置
    ##############################################

    #房间ID 建议英文 在mod_assets/location下创建的文件夹必须与ID相同 ID不允许与任何已有房间冲突
    submod_roomid = "heaven_forest"

    #房间名称 在选择房间时选择的名字
    submod_roomname = "天堂森林"

    #图片名称 若为空默认为sub_day_n 所有图片都位于<mod_assets/location/房间ID/>内
    #如id为"sub_bg_id" 则所有图片都位于<mod_assets/location/sub_bg_id/>
    #所有图片大小必须为1280*720
    #建议使用PS处理透明图层
    #####白天##### 
    sub_day = "heaven_forest.png" #晴天*必填
    sub_rain = "" #雨天
    sub_overcast = "" #多云
    sub_snow = "" #雪天

    #####晚上#####
    sub_day_n = "" #晴天 若为空则为sub_day
    sub_rain_n = "" #雨天
    sub_overcast_n = "" #多云
    sub_snow_n = "" #雪天

    #####傍晚#####
    sub_day_ss = "" #晴天
    sub_rain_ss = "" #雨天
    sub_overcast_ss = "" #多云
    sub_snow_ss = "" #雪天

    ##############################################
    # 房间细节 True=是,False=否
    ##############################################

    #禁用天气变化
    sub_dp = True
    #隐藏日历
    sub_hc = True
    #禁用天气动画
    sub_hm = True
    #是否解锁
    sub_unl = False 


    #除非你知道在做什么,否则不要动以下代码!============================
    #定义图片文件夹
    imgdir = "mod_assets/location/"+ submod_roomid + "/"
    if not renpy.loadable(imgdir + sub_day):
        raise Exception("sub_day could not be loaded, please check the file name - sub_day无法加载，请检查文件名称")
    def DetectBg(imgname,weather):
        """
        检测指定天气房间图片是否存在
        imgname - 要检查的图片,
        weather - 若图片加载失败/未填 "d" ->sub_day  n ->sub_day_n
        """
        if sub_day == "" or sub_day == Null:
            raise Exception("sub_day cannot be an empty string - sub_day不可为空,你至少要有一张图,对吧?")
            return
        if imgname == "" and renpy.loadable(imgdir + imgname):
            if weather == "d":
                return imgdir + sub_day
            elif weather == "n":
                return DetectBg(sub_day_n,"d")
            else:
                raise Exception("weather must be \"d\"/\"n\" - weather 必须为“d”或“n”,你修改了别的位置了是吧?")
        elif renpy.loadable(imgdir + imgname):
            return imgdir + imgname
        else:
            raise Exception("Background resources folder not found - 背景资源文件夹未找到,请检查对应的id和文件夹是否正确创建")


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
image heaven_forest_day = imgdir + sub_day 
image heaven_forest_rain = DetectBg(sub_rain,"n")
image heaven_forest_overcast = DetectBg(sub_overcast,"n")
image heaven_forest_snow = DetectBg(sub_snow,"n")

# 晚上
image heaven_forest_night= DetectBg(sub_day_n,"n")          
image heaven_forest_rain_night = DetectBg(sub_rain_n,"n")
image heaven_forest_overcast_night = DetectBg(sub_overcast_n,"n")
image heaven_forest_snow_night = DetectBg(sub_snow_n,"n")

# 傍晚
image heaven_forest_ss = DetectBg(sub_day_ss,"d")
image heaven_forest_rain_ss = DetectBg(sub_rain_ss,"n")
image heaven_forest_overcast_ss = DetectBg(sub_overcast_ss,"n")
image heaven_forest_snow_ss = DetectBg(sub_snow_ss,"n")

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
    heaven_forest_Furnished_spaceroom3 = MASFilterableBackground(
        submod_roomid,
        submod_roomname,
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

        disable_progressive=sub_dp,    #是否禁用天气变化
        hide_masks=sub_hm,             #是否禁用天气动画
        hide_calendar=sub_hc,          #是否隐藏日历
        unlocked=sub_unl,                #是否解锁
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
            if not store.mas_inEVL("switch_dlg"):
                store.pushEvent("switch_dlg")

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

        if _new == store.mas_background_def:
            store.pushEvent("return_switch_dlg")


##############################################
# 选择对话
##############################################

###进入这个房间后随机选择一句
label switch_dlg:
    python:
        switch_quip = renpy.substitute(renpy.random.choice([
            "她的房间真有少女气息呢~",
            "呜哇，老是来别人的房间，有空的话...也来我家坐坐吧~",
            "小飞鱼很可爱~",
            "她真的很开心呢..."
        ]))

    m 1hua "[switch_quip]"

    return
###回到默认教室以后随机选择一句
label return_switch_dlg:
    python:
        switch_quip = renpy.substitute(renpy.random.choice([
            "我回来了~",
            "想念我们的教室了?",
            "我们已经在一起多久了呢..."
        ]))

    m 1hua "[switch_quip]"
    return

### ---//从这里的代码到末尾的代码可以考虑删除,因为只是一些对话代码//---
