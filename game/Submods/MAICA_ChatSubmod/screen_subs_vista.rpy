init python:
    def maica_upload_new_image():
        import file_selector
        image = file_selector.select_file()
        if image:
            try:
                store.maica.upload_vista_image(image)
            except Exception as e:
                renpy.notify(_("MAICA: Upload failed"))

        else:
            renpy.notify(_("MAICA: No image chosen"))

    def maica_reupload_image(uuid):
        try:
            store.maica.reupload_vista_image(uuid)
            renpy.notify(_("MAICA: Re-upload success"))
        except Exception as e:
            renpy.notify(_("MAICA: Re-upload failed"))

    def maica_upload_image_android_submit(image_path):
        try:
            store.maica.upload_vista_image(image_path)
            renpy.notify(_("MAICA: Upload success"))
        except Exception as e:
            renpy.notify(_("MAICA: Upload failed"))
        renpy.hide_screen("maica_upload_image_android")

    def remove_if_selected(item):
        if item in store._maica_selected_visuals:
            store._maica_selected_visuals.remove(item)
screen maica_upload_image_android():
    default imageselector = select_image()
    modal True
    zorder 100

    use maica_common_outer_frame():
        use maica_common_inner_frame():
            if imageselector.is_selecting:
                text _("Selecting images...")
            else:
                if imageselector.image_path:
                    text maica_escape_display_text(renpy.substitute(
                        _("Image chosen: [imageselector.image_path]"),
                        scope={"imageselector": imageselector}
                    ))
                else:
                    text _("No image chosen")
        hbox:
            xpos 10
            style_prefix "confirm"
            if imageselector.image_path:
                textbutton _("Upload"):
                    action Function(maica_upload_image_android_submit, imageselector.image_path)
            textbutton _("Close{#maica_host_close}"):
                action [Hide("maica_upload_image_android"), NullAction()]

screen maica_vista_filelist(selecting=False):
    python:
        import time
        files = store.maica.maica_instance.vista_manager.export_list()
        #store.maica.maica_instance.vista_manager.list_remote()
        def is_expired(item):
            global files
            index = files.index(item)
            if index >= 3:
                return True
            return time.time() - item['upload_time'] > 28800# or item['uuid'] in store.maica.maica_instance.vista_manager.cloud_files

        def selected_is_full():
            return len(store._maica_selected_visuals) >= 3

        def format_timestamp(timestamp):
            """将时间戳转换为可读的时间格式

            Args:
                timestamp: Unix时间戳

            Returns:
                格式化的时间字符串 (YYYY-MM-DD HH:MM:SS)
            """
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

    modal True
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():
            style_prefix "generic_fancy_check"
            if renpy.android:
                text _("Android devices may experience temporary display issues after uploading.")
            for item in files:
                use maica_l2_subframe():
                    text renpy.substitute(_("Uploaded at: ")) + "{}".format(format_timestamp(item['upload_time']))
                    if renpy.config.debug:
                        text "UUID: {}".format(item['uuid'])
                    if is_expired(item):
                        text _("This file is outdated")
                    else:
                        text _("This file is valid")
                    hbox:
                        python:
                            preview_info = store.maica.maica_instance.vista_manager.get_thumbnail_info(item)
                        if preview_info:
                            $ img_path = preview_info[0]
                            add img_path
                        else:
                            text _("Image preview unavailable")
                    if store.maica.maica_instance.is_connected():
                        if selecting:
                            if not is_expired(item):
                                if not renpy.seen_label("maica_pre_wants_mvista"):
                                    textbutton _("! MVista not unlocked"):
                                        style "generic_fancy_check_button_disabled"
                                elif selected_is_full():
                                    textbutton _("Choose this image (limit reached)"):
                                        style "generic_fancy_check_button_disabled"
                                else:
                                    if item in store._maica_selected_visuals:
                                        textbutton _("Choose this image"):
                                            action Function(store._maica_selected_visuals.remove, item)
                                            selected True
                                    else:
                                        textbutton _("Choose this image"):
                                            action Function(store._maica_selected_visuals.append, item)
                            else:
                                textbutton _("Choose this image (outdated)"):
                                    style "generic_fancy_check_button_disabled"

                        hbox:
                            style_prefix "maica_check"
                            if not is_expired(item):
                                textbutton _("Delete this image (local and remote)"):
                                    action [Function(remove_if_selected, item),
                                        Function(store.maica.delete_vista_image, item['uuid'])]
                            else:
                                textbutton _("Delete this image (local)"):
                                    action Function(store.maica.remove_vista_image, item['uuid'])
                                textbutton _("Re-upload this image"):
                                    action [Function(maica_reupload_image, item['uuid'])]
        hbox:
            xpos 10
            style_prefix "confirm"
            if store.maica.maica_instance.is_connected():
                textbutton _("Upload new image"):
                    if renpy.android:
                        action Show("maica_upload_image_android")
                    else:
                        action Function(maica_upload_new_image)
            else:
                textbutton _("Upload new image (login required)")


            textbutton _("Close{#maica_host_close}"):
                action Hide("maica_vista_filelist")

