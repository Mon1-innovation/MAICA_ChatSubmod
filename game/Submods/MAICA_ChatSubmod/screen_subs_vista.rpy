init python:
    def maica_upload_new_image():
        import file_selector
        image = file_selector.select_file()
        if image:
            try:
                store.maica.maica_instance.vista_manager.upload(image)
            except Exception as e:
                renpy.notify(_("MAICA: Upload failed"))

        else:
            renpy.notify(_("MAICA: No image chosen"))

    def maica_reupload_image(uuid):
        try:
            store.maica.maica_instance.vista_manager.reupload(uuid)
            renpy.notify(_("MAICA: Re-upload success"))
        except Exception as e:
            renpy.notify(_("MAICA: Re-upload failed"))

    def maica_upload_image_android_submit(image_path):
        try:
            store.maica.maica_instance.vista_manager.upload(image_path)
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
                    text _("Image chosen: [imageselector.image_path]")
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

        def get_scaled_size(xy, max_width=600, max_height=300):
            """等比例缩放图片尺寸（过大则缩小，过小则拉伸）

            Args:
                xy: 原始尺寸元组 (width, height)
                max_width: 目标最大宽度
                max_height: 目标最大高度

            Returns:
                缩放后的尺寸元组 (width, height)
            """
            width, height = xy

            # 计算宽度和高度的缩放比例
            width_ratio = float(max_width) / float(width)
            height_ratio = float(max_height) / float(height)

            # 选择较小的比例以确保等比例缩放后两个维度都不超过最大值
            scale_ratio = min(width_ratio, height_ratio)

            # 计算缩放后的尺寸
            new_width = int(width * scale_ratio)
            new_height = int(height * scale_ratio)

            return (new_width, new_height)

        def format_timestamp(timestamp):
            """将时间戳转换为可读的时间格式

            Args:
                timestamp: Unix时间戳

            Returns:
                格式化的时间字符串 (YYYY-MM-DD HH:MM:SS)
            """
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

        def get_display_image(item):
            """获取要显示的图片路径（优先缩略图）

            Args:
                item: 文件项字典

            Returns:
                (image_path, exists) 元组
            """
            import os
            thumb = item.get('thumb_path')
            if thumb and (os.path.exists(thumb) or renpy.android):
                return (thumb, True)
            path = item.get('path')
            if path and os.path.exists(path):
                return (path, True)
            return (None, False)

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
                            img_path, img_exists = get_display_image(item)
                        if img_exists:
                            add Transform(img_path, size=get_scaled_size((item['width'], item['height'])))
                        else:
                            text _("Image file does not exist: [img_path]")
                    if store.maica.maica_instance.is_connected():
                        if selecting:
                            if not is_expired(item):
                                if not persistent._maica_vista_enabled:
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
                                        Function(store.maica.maica_instance.vista_manager.delete, item['uuid'])]
                            else:
                                textbutton _("Delete this image (local)"):
                                    action Function(store.maica.maica_instance.vista_manager.remove, item['uuid'])
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

