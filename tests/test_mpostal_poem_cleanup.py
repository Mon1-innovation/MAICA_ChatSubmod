from pathlib import Path


def test_mpostal_response_poem_is_removed_after_display():
    main_source = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "main.rpy"
    ).read_text(encoding="utf-8")
    show_label = main_source[
        main_source.index('label maica_mpostal_show(content = "no content"):'):
        main_source.index("label maica_mpostal_show_backtoscreen")
    ]

    display_call = 'call mas_showpoem(store._MP, "mod_assets/poem_assets/mail_maica_bg.png")'
    poem_map_removal = "store.mas_poems.poem_map.pop(store._MP.poem_id, None)"
    seen_removal = "persistent._mas_poems_seen.pop(store._MP.poem_id, None)"

    assert display_call in show_label
    assert poem_map_removal in show_label
    assert seen_removal in show_label
    assert show_label.index(display_call) < show_label.index(poem_map_removal)
    assert show_label.index(poem_map_removal) < show_label.index(seen_removal)


def test_mpostal_reread_uses_the_game_scene_and_restores_the_history_menu():
    root = Path(__file__).resolve().parents[1]
    main_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "main.rpy"
    ).read_text(encoding="utf-8")
    screen_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "screen_subs.rpy"
    ).read_text(encoding="utf-8")

    back_to_screen = main_source[
        main_source.index("label maica_mpostal_show_backtoscreen"):
        main_source.index("label _maica_return_game_menu")
    ]
    for screen_name in (
        "maica_mpostals",
        "maica_setting",
        "maica_setting_tooltip",
        "submods",
    ):
        assert "hide screen {}".format(screen_name) in back_to_screen
    assert "with None" in back_to_screen
    assert "call maica_mpostal_show(content)" in back_to_screen

    reread_menu = screen_source[
        screen_source.index("screen maica_mpostals():"):
        screen_source.index("screen maica_support():")
    ]
    assert reread_menu.count("_maica_call_in_new_context_preserve_layers") == 2
    reread_actions = reread_menu[
        reread_menu.index('textbutton _("Read [player]'):
        reread_menu.index('if postal["responsed_status"]')
    ]
    assert "Hide(\"maica_mpostals\")" not in reread_actions

    # The old event-queue callback reopened the settings context after a poem.
    assert "label maica_mpostal_show_mpscreen" not in main_source
    assert 'functionplugin("maica_mpostal_show_backtoscreen")' not in main_source


def test_mpostal_receipt_stages_attachment_before_removing_mail():
    root = Path(__file__).resolve().parents[1]
    api_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "api.rpy"
    ).read_text(encoding="utf-8")
    intake = api_source[
        api_source.index("def find_mail_files():"):
        api_source.index("def has_mail_waitsend():")
    ]

    stage = "image_file = store.maica.stage_mpostal_image(image_path)"
    remove_mail = "os.remove(file_path)"
    append_record = "mail_files.append({"
    assert stage in intake
    assert '"attachment_path": image_file' in intake
    assert intake.index(stage) < intake.index(remove_mail) < intake.index(append_record)
    assert "_mpostal_attachment_store().restore(image_file, image_path)" in intake


def test_mpostal_original_and_preview_have_separate_cleanup_lifetimes():
    root = Path(__file__).resolve().parents[1]
    api_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "api.rpy"
    ).read_text(encoding="utf-8")
    main_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "main.rpy"
    ).read_text(encoding="utf-8")
    screen_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "screen_subs.rpy"
    ).read_text(encoding="utf-8")

    read_flow = main_source[
        main_source.index("label maica_mpostal_read:"):
        main_source.index("label maica_mpostal_read.failed:")
    ]
    success_guard = (
        'if _return == "success" and '
        'cur_postal["responsed_status"] == "received":'
    )
    assert success_guard in read_flow
    assert "store.maica.delete_mpostal_original(cur_postal)" in read_flow
    assert "delete_mpostal_preview" not in read_flow
    assert read_flow.index("if ai.is_failed():") < read_flow.index(success_guard)

    original_cleanup = api_source[
        api_source.index("def delete_mpostal_original(postal):"):
        api_source.index("def delete_mpostal_preview(postal):")
    ]
    preview_cleanup = api_source[
        api_source.index("def delete_mpostal_preview(postal):"):
        api_source.index("def prepare_mpostal_preview(postal):")
    ]
    assert "delete_thumbnail" not in original_cleanup
    assert "delete_thumbnail(preview)" in preview_cleanup

    postal_screen = screen_source[
        screen_source.index("screen maica_mpostals():"):
        screen_source.index("screen maica_support():")
    ]
    assert "store.maica.delete_mpostal_record_files(postal)" in postal_screen
    assert "Function(_delete_postal, postal)" in postal_screen
    assert "if item is postal:" in postal_screen
    assert postal_screen.index("pop(index)") < postal_screen.index(
        "delete_mpostal_record_files(postal)"
    )
    assert "postal[\"raw_title\"]" not in postal_screen[
        postal_screen.index('textbutton _("Delete")'):
    ]


def test_mpostal_list_prefers_its_record_owned_preview():
    root = Path(__file__).resolve().parents[1]
    api_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "api.rpy"
    ).read_text(encoding="utf-8")
    screen_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "screen_subs.rpy"
    ).read_text(encoding="utf-8")

    prepare_preview = api_source[
        api_source.index("def prepare_mpostal_preview(postal):"):
        api_source.index("def prepare_image_previews():")
    ]
    assert prepare_preview.index('postal.get("raw_image_preview")') < prepare_preview.index(
        'postal.get("vista_image_info")'
    )
    assert 'postal.pop("raw_image_preview"' not in prepare_preview

    postal_screen = screen_source[
        screen_source.index("screen maica_mpostals():"):
        screen_source.index("screen maica_support():")
    ]
    assert postal_screen.index("postal.get('raw_image_preview')") < postal_screen.index(
        "postal.get('vista_image_info')"
    )


def test_mpostal_startup_adopts_only_known_legacy_attachment_roots():
    api_source = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "api.rpy"
    ).read_text(encoding="utf-8")
    adoption = api_source[
        api_source.index("def adopt_legacy_mpostal_image(postal):"):
        api_source.index("def delete_mpostal_original(postal):")
    ]
    startup = api_source[
        api_source.index("def prepare_image_previews():"):
        api_source.index("maica_basedir =")
    ]

    assert "path_is_within" in adoption
    assert "in_characters" in adoption
    assert "in_legacy_cache" in adoption
    assert 'os.path.splitext(raw_image)[1].lower() != ".mms"' in adoption
    assert "if in_characters and os.path.exists" in adoption
    assert startup.index("adopt_legacy_mpostal_image(postal)") < startup.index(
        "prepare_mpostal_preview(postal)"
    )
    assert "store.maica.prepare_image_previews()" in api_source
