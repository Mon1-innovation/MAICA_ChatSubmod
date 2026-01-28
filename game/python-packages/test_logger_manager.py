# -*- coding: utf-8 -*-
"""
Test suite for LoggerManager runtime modifications and synchronization.

Tests cover:
- Singleton pattern verification
- Runtime log level modifications
- Handler management
- Formatter modifications
- Injection point synchronization
- MultiLoggerWrapper functionality
- Backward compatibility
"""

import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger_manager import (
    LoggerManager, get_logger_manager, get_logger,
    LoggerWrapper, MultiLoggerWrapper
)


class TestLoggerManager(object):
    """Test cases for LoggerManager"""

    def test_singleton_pattern(self):
        """Verify LoggerManager is a singleton"""
        manager1 = get_logger_manager()
        manager2 = get_logger_manager()
        assert manager1 is manager2, "LoggerManager should be singleton"
        print("✓ Singleton pattern test passed")

    def test_initial_logger_state(self):
        """Verify initial logger state"""
        manager = get_logger_manager()
        assert manager.logger is not None, "Logger should not be None"
        assert manager.logger.level == logging.DEBUG, "Initial level should be DEBUG"
        assert len(manager.logger.handlers) > 0, "Logger should have at least one handler"
        print("✓ Initial logger state test passed")

    def test_get_logger_function(self):
        """Verify get_logger() function returns correct logger"""
        logger = get_logger()
        assert logger is not None, "get_logger() should return a logger"
        manager = get_logger_manager()
        assert logger is manager.logger, "get_logger() should return manager's logger"
        print("✓ get_logger() function test passed")

    def test_set_log_level(self):
        """Verify log level modification works"""
        manager = get_logger_manager()

        # Test setting to WARNING
        manager.set_log_level(logging.WARNING)
        assert manager.logger.level == logging.WARNING, "Level should be WARNING"

        # Test setting to INFO
        manager.set_log_level(logging.INFO)
        assert manager.logger.level == logging.INFO, "Level should be INFO"

        # Reset to DEBUG for other tests
        manager.set_log_level(logging.DEBUG)
        print("✓ Set log level test passed")

    def test_add_remove_handler(self):
        """Verify handler addition and removal"""
        manager = get_logger_manager()
        initial_count = len(manager.logger.handlers)

        # Create a test handler
        test_handler = logging.StreamHandler()
        test_handler.setLevel(logging.DEBUG)

        # Test adding handler
        manager.add_handler(test_handler)
        assert len(manager.logger.handlers) == initial_count + 1, "Handler should be added"

        # Test removing handler
        manager.remove_handler(test_handler)
        assert len(manager.logger.handlers) == initial_count, "Handler should be removed"
        print("✓ Add/remove handler test passed")

    def test_set_formatter(self):
        """Verify formatter modification"""
        manager = get_logger_manager()

        # Test setting custom formatter
        custom_fmt = "%(name)s - %(levelname)s - %(message)s"
        custom_datefmt = "%Y/%m/%d %H:%M:%S"
        manager.set_formatter(custom_fmt, custom_datefmt)

        # Verify formatter was set
        assert manager._formatter is not None, "Formatter should be set"
        assert custom_fmt in str(manager._formatter._fmt), "Format string should be updated"
        print("✓ Set formatter test passed")

    def test_get_status(self):
        """Verify get_status() returns proper information"""
        manager = get_logger_manager()
        status = manager.get_status()

        assert 'logger_level' in status, "Status should have logger_level"
        assert 'handler_count' in status, "Status should have handler_count"
        assert 'handlers' in status, "Status should have handlers list"
        assert 'formatter' in status, "Status should have formatter"
        assert 'injected_references' in status, "Status should have injected_references"
        print("✓ Get status test passed")
        print("  Status: {}".format(status))

    def test_injection_point_registration(self):
        """Verify injection point registration"""
        manager = get_logger_manager()

        # Create test module
        class TestModule:
            logger = None

        test_module = TestModule()
        test_module.logger = manager.logger

        # Register injection point
        manager.register_injected_reference('test_module.logger', test_module, 'logger')
        assert 'test_module.logger' in manager._injected_references, "Injection point should be registered"
        print("✓ Injection point registration test passed")

    def test_logger_wrapper(self):
        """Verify LoggerWrapper functionality"""
        wrapper = LoggerWrapper()

        # Test that wrapper delegates to manager's logger
        assert wrapper.logger is get_logger_manager().logger, "Wrapper should return manager's logger"

        # Test logging methods
        try:
            wrapper.debug("Test debug message")
            wrapper.info("Test info message")
            wrapper.warning("Test warning message")
            wrapper.error("Test error message")
            print("✓ LoggerWrapper test passed")
        except Exception as e:
            print("✗ LoggerWrapper test failed: {}".format(e))
            raise

    def test_multi_logger_wrapper(self):
        """Verify MultiLoggerWrapper functionality"""
        logger1 = logging.getLogger("test1")
        logger2 = logging.getLogger("test2")

        wrapper = MultiLoggerWrapper([logger1, logger2])

        # Test adding loggers
        logger3 = logging.getLogger("test3")
        wrapper.add_logger(logger3)
        assert logger3 in wrapper._loggers, "Logger should be added to wrapper"

        # Test removing loggers
        wrapper.remove_logger(logger3)
        assert logger3 not in wrapper._loggers, "Logger should be removed from wrapper"

        # Test logging to all
        try:
            wrapper.debug("Test message to all")
            wrapper.info("Test info to all")
            wrapper.warning("Test warning to all")
            wrapper.error("Test error to all")
            print("✓ MultiLoggerWrapper test passed")
        except Exception as e:
            print("✗ MultiLoggerWrapper test failed: {}".format(e))
            raise

    def test_runtime_modification_synchronization(self):
        """Verify runtime modifications sync properly"""
        manager = get_logger_manager()

        # Create a test module with logger
        class TestModule:
            logger_level = None

        test_module = TestModule()
        test_module.logger = manager.logger
        initial_level = test_module.logger.level

        # Modify log level
        manager.set_log_level(logging.WARNING)

        # Sync should maintain the update
        assert manager.logger.level == logging.WARNING, "Manager logger level should be WARNING"
        assert test_module.logger.level == logging.WARNING, "Test module logger level should be WARNING"

        # Reset
        manager.set_log_level(logging.DEBUG)
        print("✓ Runtime modification synchronization test passed")

    def test_backward_compatibility(self):
        """Verify backward compatibility with old logger usage"""
        import bot_interface

        # Test that bot_interface.logger is available
        assert hasattr(bot_interface, 'logger'), "bot_interface should have logger attribute"
        assert bot_interface.logger is not None, "bot_interface.logger should not be None"

        # Test that bot_interface._logger_manager is available
        assert hasattr(bot_interface, '_logger_manager'), "bot_interface should have _logger_manager"

        # Test logging through bot_interface.logger
        try:
            bot_interface.logger.info("Test compatibility message")
            print("✓ Backward compatibility test passed")
        except Exception as e:
            print("✗ Backward compatibility test failed: {}".format(e))
            raise


def run_all_tests():
    """Run all tests"""
    test_suite = TestLoggerManager()

    tests = [
        ("Singleton Pattern", test_suite.test_singleton_pattern),
        ("Initial Logger State", test_suite.test_initial_logger_state),
        ("Get Logger Function", test_suite.test_get_logger_function),
        ("Set Log Level", test_suite.test_set_log_level),
        ("Add/Remove Handler", test_suite.test_add_remove_handler),
        ("Set Formatter", test_suite.test_set_formatter),
        ("Get Status", test_suite.test_get_status),
        ("Injection Point Registration", test_suite.test_injection_point_registration),
        ("Logger Wrapper", test_suite.test_logger_wrapper),
        ("Multi Logger Wrapper", test_suite.test_multi_logger_wrapper),
        ("Runtime Modification Sync", test_suite.test_runtime_modification_synchronization),
        ("Backward Compatibility", test_suite.test_backward_compatibility),
    ]

    print("=" * 60)
    print("Running LoggerManager Test Suite")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print("\n[{}] {}".format(len([1 for _ in range(passed + failed + 1)]), test_name))
            test_func()
            passed += 1
        except Exception as e:
            print("✗ {} test failed: {}".format(test_name, e))
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print("Test Results: {} passed, {} failed".format(passed, failed))
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
