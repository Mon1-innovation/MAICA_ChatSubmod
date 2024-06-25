init 5 python in maica:
    def change_token(content):
        return True, content
    store.mas_registerAPIKey(
        "Maica_Token",
        "Maica 令牌",
        on_change=change_token
    )

    import maica
    maica = maica.Maica("", "")