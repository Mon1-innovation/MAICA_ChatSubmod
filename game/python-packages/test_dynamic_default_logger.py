# -*- coding: utf-8 -*-
"""
Test for DynamicDefaultLogger functionality

验证 default_logger 能够动态获取最新的 logger 配置
"""

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger_manager import get_logger_manager
import maica_tasker


def test_dynamic_default_logger():
    """测试 DynamicDefaultLogger 动态获取最新 logger"""
    print("=" * 60)
    print("Testing DynamicDefaultLogger")
    print("=" * 60)

    manager = get_logger_manager()

    # Test 1: 初始状态下的日志记录
    print("\n[Test 1] Initial state - logging at DEBUG level")
    maica_tasker.default_logger.debug("This is a debug message")
    maica_tasker.default_logger.info("This is an info message")

    # Test 2: 修改日志级别，验证 default_logger 获取最新配置
    print("\n[Test 2] Changing log level to WARNING")
    manager.set_log_level(logging.WARNING)
    print("Log level changed. Now trying to log debug message (should not appear):")
    maica_tasker.default_logger.debug("This debug message should NOT appear")
    print("Logging warning message (should appear):")
    maica_tasker.default_logger.warning("This warning message SHOULD appear")

    # Test 3: 恢复日志级别
    print("\n[Test 3] Restoring log level to DEBUG")
    manager.set_log_level(logging.DEBUG)
    print("Log level restored. Logging debug message (should appear now):")
    maica_tasker.default_logger.debug("This debug message SHOULD appear after restore")

    # Test 4: 测试其他日志方法
    print("\n[Test 4] Testing all logger methods")
    maica_tasker.default_logger.debug("Debug message")
    maica_tasker.default_logger.info("Info message")
    maica_tasker.default_logger.warning("Warning message")
    maica_tasker.default_logger.error("Error message")
    maica_tasker.default_logger.critical("Critical message")

    # Test 5: 验证 default_logger 是 DynamicDefaultLogger 实例
    print("\n[Test 5] Type verification")
    assert isinstance(maica_tasker.default_logger, maica_tasker.DynamicDefaultLogger), \
        "default_logger should be DynamicDefaultLogger instance"
    print("✓ default_logger is DynamicDefaultLogger instance")

    # Test 6: 验证代理到 LoggerManager 的 logger
    print("\n[Test 6] Verify delegation to LoggerManager")
    current_logger = maica_tasker.default_logger._get_current_logger()
    manager_logger = manager.logger
    assert current_logger is manager_logger, \
        "default_logger should delegate to manager's logger"
    print("✓ default_logger correctly delegates to LoggerManager")

    # Test 7: 验证属性代理（__getattr__）
    print("\n[Test 7] Verify attribute delegation")
    # 测试访问 level 属性
    level = maica_tasker.default_logger.level
    assert level == manager.logger.level, \
        "default_logger.level should match manager's logger level"
    print("✓ default_logger correctly delegates attributes to logger")
    print("  Current log level: {}".format(logging.getLevelName(level)))

    print("\n" + "=" * 60)
    print("All DynamicDefaultLogger tests passed! ✓")
    print("=" * 60)


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n" + "=" * 60)
    print("Testing Backward Compatibility")
    print("=" * 60)

    # 测试模块中直接访问 default_logger
    print("\n[Test] Direct access to default_logger in module")
    try:
        maica_tasker.default_logger.info("Backward compatibility test message")
        print("✓ Direct access works")
    except Exception as e:
        print("✗ Direct access failed: {}".format(e))
        raise

    print("\n" + "=" * 60)
    print("Backward compatibility verified! ✓")
    print("=" * 60)


def test_maica_task_logger_property():
    """测试 MaicaTask 类的 logger property"""
    print("\n" + "=" * 60)
    print("Testing MaicaTask.logger property")
    print("=" * 60)

    # 创建一个简单的测试任务（不需要初始化复杂的依赖）
    class SimpleTask(maica_tasker.MaicaTask):
        def on_event(self, event):
            pass

    manager = maica_tasker.MaicaTaskManager()

    print("\n[Test] Creating task and accessing logger")
    try:
        # 直接创建任务（不注册到管理器）
        task = SimpleTask(None)

        # 访问 logger property
        task_logger = task.logger
        assert task_logger is not None, "Task logger should not be None"

        # 验证它返回的是 default_logger
        assert task_logger is maica_tasker.default_logger, \
            "Task logger should return module's default_logger"

        print("✓ MaicaTask.logger property works correctly")
    except Exception as e:
        print("✗ MaicaTask.logger property test failed: {}".format(e))
        raise

    print("\n" + "=" * 60)
    print("MaicaTask logger property verified! ✓")
    print("=" * 60)


if __name__ == "__main__":
    test_dynamic_default_logger()
    test_backward_compatibility()
    test_maica_task_logger_property()
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✓✓✓")
    print("=" * 60)
