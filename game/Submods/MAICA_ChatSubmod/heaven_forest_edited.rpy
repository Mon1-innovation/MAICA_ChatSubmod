
image hf2_weather_fb = MASFallbackFilterDisplayable(
    day="mod_assets/location/heaven_forest_2/d.png",
    sunset="mod_assets/location/heaven_forest_2/ss.png",
    night="mod_assets/location/heaven_forest_2/n.png",
)

init -1 python:
    hf2_weather = MASFilterableWeather(
        "hf2_weather_id",
        "hf2_weather_label",
        img_tag="hf2_weather_fb",
        precip_type=store.mas_weather.PRECIP_TYPE_DEF,
        unlocked=False
    )
    heaven_forest_d = MASFilterableBackground(
        # ID
        "heaven_forest_d",
        "heaven_forest_d",

        # mapping of filters to MASWeatherMaps
        MASFilterWeatherMap(
            day=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "hf2_weather_fb",
                store.mas_weather.PRECIP_TYPE_RAIN: "hf2_weather_fb",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "hf2_weather_fb",
                store.mas_weather.PRECIP_TYPE_SNOW: "hf2_weather_fb",
            }),
            night=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "hf2_weather_fb",
                store.mas_weather.PRECIP_TYPE_SNOW: "hf2_weather_fb",
            }),
            sunset=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "hf2_weather_fb",
                store.mas_weather.PRECIP_TYPE_RAIN: "hf2_weather_fb",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "hf2_weather_fb",
                store.mas_weather.PRECIP_TYPE_SNOW: "hf2_weather_fb",
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

        disable_progressive=True,
        unlocked=True,
        entry_pp=store.mas_background._def_background_entry,
        exit_pp=store.mas_background._def_background_exit,
    )




