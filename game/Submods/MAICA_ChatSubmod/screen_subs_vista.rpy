init python:
    def maica_upload_new_image():
        import file_selector
        image = file_selector.select_file()
        if image:
            store.maica.maica.vista_manager.upload(image)
        else:
            renpy.notify("未选择图片")
screen maica_vista_filelist(selecting=False):
    python:
        import time
        files = store.maica.maica.vista_manager.export_list()
        def is_expired(item):
            global files
            index = files.index(item)
            if index >= 3:
                return True
            return time.time() - item['upload_time'] > 28800

    modal True
    zorder 92

    use maica_common_outer_frame():
        use maica_common_inner_frame():
            style_prefix "generic_fancy_check"


        
            for item in files:
                text "time: {}".format(item['upload_time'])
                text "uuid: {}".format(item['uuid'])
                if is_expired(item):
                    text "该文件已过期"
                else:
                    text "该文件尚未过期"
                add item['path']
                if store.maica.maica.is_connected():
                    if True:
                        if not is_expired(item):
                            textbutton _("选中这张图片")
                            textbutton _("在服务器上删除这张图片"):
                                action Function(store.maica.maica.vista_manager.delete, item['uuid'],)
                        else:
                            textbutton _("选中这张图片 [[图片已经过期, 请重新上传]")
                            textbutton _("删除这张图片 [[仅删除本地记录]"):
                                action Function(store.maica.maica.vista_manager.remove, item['uuid'],)
                            textbutton _("重新上传这张图片"):
                                action Function(store.maica.maica.vista_manager.reupload, item['uuid'],)

            hbox:
                xpos 10
                style_prefix "confirm"
                if store.maica.maica.is_connected():
                    textbutton _("上传新图片"):
                        action Function(maica_upload_new_image)
                else:
                    textbutton _("上传新图片 [[请先登录]")


                textbutton _("关闭"):
                    action Hide("maica_vista_filelist")

