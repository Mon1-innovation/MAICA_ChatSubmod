init python:
    def maica_upload_new_image():
        import file_selector
        image = file_selector.select_file()
        if image:
            store.maica.maica.vista_manager.upload(image)
        else:
            renpy.notify("未选择图片")

    def maica_reupload_image(uuid):
        try:
            store.maica.maica.vista_manager.reupload(uuid)
            renpy.notify("重新上传成功")
        except Exception as e:
            renpy.notify("重新上传失败")

    def maica_upload_image_android_submit(image_path):
        try:
            store.maica.maica.vista_manager.upload(image_path)
            renpy.notify("上传成功")
        except Exception as e:
            renpy.notify("上传失败")
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
                text "正在选择图片..."
            else:
                if imageselector.image_path:
                    text "已选择: [imageselector.image_path]"
                else:
                    text "未选择图片"
        hbox:
            xpos 10
            style_prefix "confirm"
            if imageselector.image_path:
                textbutton _("上传"):
                    action Function(maica_upload_image_android_submit, imageselector.image_path)
            textbutton _("关闭"):
                action [Hide("maica_upload_image_android"), NullAction()]
    
screen maica_vista_filelist(selecting=False):
    python:
        import time
        files = store.maica.maica.vista_manager.export_list()
        #store.maica.maica.vista_manager.list_remote()
        def is_expired(item):
            global files
            index = files.index(item)
            if index >= 3:
                return True
            return time.time() - item['upload_time'] > 28800# or item['uuid'] in store.maica.maica.vista_manager.cloud_files

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
                text _("Android设备上传图片可能有短暂的显示异常.")
            for item in files:
                text renpy.substitute(_("上传时间: ")) + "{}".format(format_timestamp(item['upload_time']))
                text "UUID: {}".format(item['uuid'])
                if is_expired(item):
                    text _("该文件已过期")
                else:
                    text _("该文件尚未过期")
                hbox:
                    python:
                        img_path, img_exists = get_display_image(item)
                    if img_exists:
                        add Transform(img_path, size=get_scaled_size((item['width'], item['height'])))
                    else:
                        text _("图片文件不存在: [img_path]")
                if store.maica.maica.is_connected():
                    if selecting:
                        if not is_expired(item):
                            if not persistent._maica_vista_enabled:
                                textbutton _("! MVista尚未解锁"):
                                    style "generic_fancy_check_button_disabled"
                            elif selected_is_full():
                                textbutton _("选中这张图片 (数量已满)"):
                                    style "generic_fancy_check_button_disabled"
                            else:
                                if item in store._maica_selected_visuals:
                                    textbutton _("选中这张图片"):
                                        action Function(store._maica_selected_visuals.remove, item)
                                        selected True
                                else:
                                    textbutton _("选中这张图片"):
                                        action Function(store._maica_selected_visuals.append, item)
                        else:
                            textbutton _("选中这张图片 (已过期)"):
                                style "generic_fancy_check_button_disabled"

                    hbox:
                        style_prefix "maica_check"
                        if not is_expired(item):
                            textbutton _("删除这张图片 (本地和远程)"):
                                action [Function(remove_if_selected, item),
                                    Function(store.maica.maica.vista_manager.delete, item['uuid'])]
                        else:
                            textbutton _("删除这张图片 (仅本地)"):
                                action Function(store.maica.maica.vista_manager.remove, item['uuid'])
                            textbutton _("重新上传这张图片"):
                                action [Function(maica_reupload_image, item['uuid'])]
        hbox:
            xpos 10
            style_prefix "confirm"
            if store.maica.maica.is_connected():
                textbutton _("上传新图片"):
                    if renpy.android:
                        action Show("maica_upload_image_android")
                    else:
                        action Function(maica_upload_new_image)
            else:
                textbutton _("上传新图片 (请先登录)")


            textbutton _("关闭"):
                action Hide("maica_vista_filelist")

