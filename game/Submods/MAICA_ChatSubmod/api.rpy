init 5 python in maica:
    import store
    def change_token(content):
        return True, content
    store.mas_registerAPIKey(
        "Maica_Token",
        "Maica 令牌",
        on_change=change_token
    )

    import maica
    maica = maica.MaicaAi("", "", store.mas_getAPIKey("Maica_Token"))

    #set: store.mas_api_keys.api_keys |= {"Maica_Token":token}
    # store.mas_api_keys.save_keys()