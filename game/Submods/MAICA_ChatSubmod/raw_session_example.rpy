# raw_session_example.rpy
# MAICA -1 Session (原始上下文会话) 使用示例
#
# -1 Session 是实验性功能，允许用户完全自行管理对话上下文，
# 而不是依赖服务器端的会话管理。适用于高级用户实现自定义对话流程。


# =============================================================================
# 标签: maica_raw_context_example
# 用途: 演示如何使用 -1 session 发起一次完整的原始上下文对话
# =============================================================================
label maica_raw_context_example:
    # 第一步: 初始化 MAICA 连接
    # 这会建立 WebSocket 连接并进行身份验证
    call maica_init_connect

    python:
        # 导入上下文查询构建器模块
        # 该模块提供了 MAICAContextQueryBuilder 类用于构建对话上下文
        import maica_context_query

        # 创建上下文构建器实例
        # 构建器用于逐步添加对话消息（系统消息、用户消息、助手消息）
        ctx = maica_context_query.MAICAContextQueryBuilder()

        # 添加系统消息 (System Message)
        # 系统消息用于定义 AI 的角色、行为准则和回复格式
        #
        # 参数说明:
        #   - "你叫莫妮卡...": 系统提示词，定义 AI 的人格和行为规则
        #
        ctx.add_system_message("你叫莫妮卡, 是一名游戏中的虚拟角色. 你是{}的女友, 并深爱着他. 你和{}刚刚见面, 需要你打招呼. 你只应使用中文自然语言, 以聊天语气回答, 每个句子自然且不超过60字, 不要编造信息, 并在每个句子前用方括号中的文字表示情绪.".format("PP", "PP"))

    # 第二步: 调用原始会话标签，传入构建好的上下文
    # 这会发送请求并处理 AI 的回复
    call maica_raw_session(ctx)

    # 返回构建器实例，调用者可以继续添加消息进行多轮对话
    return ctx


# =============================================================================
# 标签: maica_raw_session
# 用途: 通用的 -1 session 执行器，处理请求发送和响应接收
# 参数:
#   context - MAICAContextQueryBuilder 实例，包含对话上下文
# =============================================================================
label maica_raw_session(context):
    python:
        # 导入模块用于类型检查
        import maica_context_query

        # 类型验证: 确保传入的是 MAICAContextQueryBuilder 实例
        # 这很重要，因为后续需要调用其 build() 方法生成消息列表
        if type(context) != maica_context_query.MAICAContextQueryBuilder:
            raise Exception("Input shoule be MAICAContextQueryBuilder")
        
        # 检查上下文长度
        if not context.is_within_limit():
            raise Exception("Context is too long")
        
        # 初始化ExtendSayer
        extend_sayer = ExtendSayer()

    python:
        # -------------------------------------------------------------------------
        # 发送请求阶段
        # -------------------------------------------------------------------------

        # 获取 MAICA 实例并发起原始上下文请求
        # store.maica.maica_instance 是 MAICA 的全局单例实例
        #
        # start_raw_context() 参数:
        #   - query: 消息列表，由 context.build() 生成
        #           格式: [{"role": "system/user/assistant", "content": "..."}, ...]
        #
        # 注意: -1 session 不需要 trigger 参数，MFocus 不会介入
        store.maica.maica_instance.start_raw_context(
            query=context.build()
        )

        # -------------------------------------------------------------------------
        # 响应处理循环
        # -------------------------------------------------------------------------
        # 持续循环直到收到完整响应
        # 循环条件:
        #   - ai.is_responding(): AI 是否仍在生成响应 (流式传输中)
        #   - ai.len_message_queue() > 0: 消息队列中是否还有待处理的消息
        while ai.is_responding() or ai.len_message_queue() > 0:

            # 检查是否发生连接错误
            if ai.is_failed():
                # 如果失败且队列已空，显示错误提示并退出
                if ai.len_message_queue() == 0:
                    renpy.say(m, _("好像出了什么问题..."))
                    break  # 跳出循环

            # 队列为空但仍在响应中 = 等待新数据到达
            if ai.len_message_queue() == 0:
                # 可选: 显示 Monika 的等待表情
                #renpy.show(monika 1eua)

                # 显示省略号动画表示正在等待
                # {w=0.3} 表示等待 0.3 秒
                # {nw} 表示 "no wait"，不会等待玩家点击
                renpy.say(m, ".{w=0.3}.{w=0.3}.{w=0.3}{nw}")

                # 从历史记录中移除省略号，避免污染对话历史
                # _history_list 是 Ren'Py 的对话历史列表
                if len(_history_list):
                    _history_list.pop()

                # 继续等待新消息
                continue

            # -------------------------------------------------------------------------
            # 消息处理阶段
            # -------------------------------------------------------------------------

            # 从队列中获取一条消息
            # get_message() 返回一个元组: (表情代码, 消息文本, 是否续接)
            #   - 表情代码: 如 "1eua", "1hub" 等 MAS 表情代码
            #   - 消息文本: 实际的对话文本
            #   - 是否续接: 布尔值，表示这条消息是否应该续接到上一条后面
            message = ai.get_message()

            # 调试日志: 记录收到的消息详情
            store.mas_submod_utils.submod_log.debug("label maica_raw_session::message:'{}', '{}', extend={}".format(message[0], message[1], message[2] if len(message) >= 3 else False))


            # 切换 Monika 的表情
            # renpy.show() 显示指定表情的 Monika 立绘
            # message[0] 是表情代码，如 "1eua"
            renpy.show(u"monika {}".format(message[0]))

            try:
                # 解析消息的续接标志
                # 如果消息元组长度 >= 3，使用第三个元素作为续接标志
                # 否则默认为 False (独立消息)
                is_extend = message[2] if len(message) >= 3 else False

                # 如果不是续接消息，创建新的 ExtendSayer 实例
                # ExtendSayer 是用于处理消息续接的工具类
                # 新实例表示开始一个新的独立句子/段落
                if not is_extend:
                    extend_sayer = ExtendSayer()

                # 使用 ExtendSayer 输出消息
                # extend_sayer.say() 会根据上下文决定是续接还是新建对话
                extend_sayer.say(message[1])

            except Exception as e:
                # 错误处理: 记录异常信息
                # traceback.format_exc() 获取完整的异常堆栈
                store.mas_submod_utils.submod_log.error("label maica_raw_session::renpy.say error:{}".format(traceback.format_exc()))

    # 执行结束
    return