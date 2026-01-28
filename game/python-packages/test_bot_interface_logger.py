# -*- coding: utf-8 -*-
"""
Test suite for bot_interface dynamic logger proxy.

Verifies that:
- bot_interface.logger returns latest logger configuration each time
- Changes to log level are immediately reflected
- Changes to handlers are immediately reflected
- All modules using the logger get synchronized updates
"""

import unittest
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger_manager import get_logger_manager
from bot_interface import logger as bot_logger


class TestBotInterfaceLoggerProxy(unittest.TestCase):
    """Test the dynamic logger proxy in bot_interface"""

    def setUp(self):
        """Set up test fixtures"""
        self.logger_manager = get_logger_manager()
        # Store original state
        self.original_level = self.logger_manager.logger.level
        self.original_handlers = list(self.logger_manager.logger.handlers)

    def tearDown(self):
        """Clean up after tests"""
        # Restore original state
        self.logger_manager.logger.setLevel(self.original_level)
        # Remove extra handlers
        for handler in self.logger_manager.logger.handlers:
            if handler not in self.original_handlers:
                self.logger_manager.logger.removeHandler(handler)

    def test_logger_proxy_is_callable(self):
        """Test that bot_interface.logger proxy exists and is callable"""
        self.assertIsNotNone(bot_logger)
        # Check that core logging methods exist
        self.assertTrue(hasattr(bot_logger, 'debug'))
        self.assertTrue(hasattr(bot_logger, 'info'))
        self.assertTrue(hasattr(bot_logger, 'warning'))
        self.assertTrue(hasattr(bot_logger, 'error'))
        self.assertTrue(hasattr(bot_logger, 'critical'))

    def test_logger_proxy_methods_work(self):
        """Test that logger proxy methods execute without error"""
        try:
            bot_logger.debug("Test debug message")
            bot_logger.info("Test info message")
            bot_logger.warning("Test warning message")
            bot_logger.error("Test error message")
            bot_logger.critical("Test critical message")
        except Exception as e:
            self.fail("Logger proxy methods raised exception: {}".format(str(e)))

    def test_dynamic_log_level_change(self):
        """Test that log level changes are reflected in next call"""
        # Set to INFO level
        self.logger_manager.set_log_level(logging.INFO)
        self.assertEqual(bot_logger.getEffectiveLevel(), logging.INFO)

        # Set to DEBUG level
        self.logger_manager.set_log_level(logging.DEBUG)
        self.assertEqual(bot_logger.getEffectiveLevel(), logging.DEBUG)

        # Set to WARNING level
        self.logger_manager.set_log_level(logging.WARNING)
        self.assertEqual(bot_logger.getEffectiveLevel(), logging.WARNING)

    def test_multiple_log_level_changes(self):
        """Test multiple consecutive log level changes"""
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]

        for level in levels:
            self.logger_manager.set_log_level(level)
            # Each call to bot_logger should get the new level
            self.assertEqual(
                bot_logger.getEffectiveLevel(),
                level,
                "Log level not properly updated to {}".format(logging.getLevelName(level))
            )

    def test_handler_addition_reflected(self):
        """Test that adding handlers is immediately reflected"""
        initial_handler_count = len(self.logger_manager.logger.handlers)

        # Add a new handler
        new_handler = logging.StreamHandler()
        self.logger_manager.add_handler(new_handler)

        # Verify it's reflected in the proxy by checking via the logger manager
        self.assertEqual(
            len(self.logger_manager.logger.handlers),
            initial_handler_count + 1,
            "New handler not reflected"
        )

        # Clean up
        self.logger_manager.remove_handler(new_handler)

    def test_handler_removal_reflected(self):
        """Test that removing handlers is immediately reflected"""
        # Add a test handler first
        test_handler = logging.StreamHandler()
        self.logger_manager.add_handler(test_handler)
        handler_count_with_new = len(self.logger_manager.logger.handlers)

        # Remove the handler
        self.logger_manager.remove_handler(test_handler)

        # Verify the removal is reflected
        self.assertEqual(
            len(self.logger_manager.logger.handlers),
            handler_count_with_new - 1,
            "Handler removal not reflected"
        )

    def test_formatter_change_reflected(self):
        """Test that formatter changes are reflected"""
        new_fmt = "%(levelname)s:%(message)s"
        new_datefmt = "%Y-%m-%d"

        self.logger_manager.set_formatter(fmt=new_fmt, datefmt=new_datefmt)

        # Get current logger and check formatter
        current_logger = self.logger_manager.logger
        for handler in current_logger.handlers:
            if hasattr(handler, 'formatter') and handler.formatter:
                self.assertIn(
                    "%(levelname)s",
                    handler.formatter._fmt,
                    "Formatter not properly updated"
                )

    def test_proxy_delegates_unknown_attributes(self):
        """Test that proxy delegates unknown attributes to wrapped logger"""
        # These are standard logger attributes
        self.assertTrue(hasattr(bot_logger, 'name'))
        self.assertTrue(hasattr(bot_logger, 'parent'))
        self.assertTrue(hasattr(bot_logger, 'propagate'))

    def test_proxy_consistency_across_calls(self):
        """Test that multiple calls to proxy return consistent behavior"""
        # Set a specific log level
        self.logger_manager.set_log_level(logging.WARNING)

        # Multiple calls should all return the same level
        level1 = bot_logger.getEffectiveLevel()
        level2 = bot_logger.getEffectiveLevel()
        level3 = bot_logger.getEffectiveLevel()

        self.assertEqual(level1, level2)
        self.assertEqual(level2, level3)
        self.assertEqual(level1, logging.WARNING)

    def test_module_imports_use_same_logger(self):
        """Test that all modules using bot_interface get the same logger"""
        # Import the modules that use bot_interface.logger
        from emotion_analyze import logger as emotion_logger_1
        from emotion_analyze_v2 import logger as emotion_logger_2
        from maica_vista_files_manager import logger as vista_logger

        # Change log level
        self.logger_manager.set_log_level(logging.DEBUG)

        # All should reflect the change
        self.assertEqual(emotion_logger_1.getEffectiveLevel(), logging.DEBUG)
        self.assertEqual(emotion_logger_2.getEffectiveLevel(), logging.DEBUG)
        self.assertEqual(vista_logger.getEffectiveLevel(), logging.DEBUG)

        # Change again
        self.logger_manager.set_log_level(logging.ERROR)

        self.assertEqual(emotion_logger_1.getEffectiveLevel(), logging.ERROR)
        self.assertEqual(emotion_logger_2.getEffectiveLevel(), logging.ERROR)
        self.assertEqual(vista_logger.getEffectiveLevel(), logging.ERROR)

    def test_status_report(self):
        """Test that LoggerManager status is correct"""
        status = self.logger_manager.get_status()

        self.assertIn('logger_level', status)
        self.assertIn('handler_count', status)
        self.assertIn('handlers', status)
        self.assertIn('formatter', status)

        # Verify status shows actual state
        self.assertGreaterEqual(status['handler_count'], 1)
        self.assertIsInstance(status['handlers'], list)

    def test_concurrent_level_changes(self):
        """Test rapid successive log level changes"""
        levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
            logging.DEBUG
        ]

        for i, level in enumerate(levels):
            self.logger_manager.set_log_level(level)
            actual_level = bot_logger.getEffectiveLevel()
            self.assertEqual(
                actual_level,
                level,
                "Level mismatch at iteration {}: expected {}, got {}".format(
                    i, logging.getLevelName(level), logging.getLevelName(actual_level)
                )
            )

    def test_logger_functionality_with_proxy(self):
        """Test that actual logging works through the proxy"""
        import io
        import sys

        # Create a string buffer to capture output
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.DEBUG)

        # Set formatter
        formatter = logging.Formatter('%(levelname)s:%(message)s')
        handler.setFormatter(formatter)

        # Add to logger manager
        self.logger_manager.add_handler(handler)

        try:
            # Log a message through the proxy
            test_message = "Test logging message"
            bot_logger.info(test_message)

            # Get output
            output = stream.getvalue()
            self.assertIn(test_message, output)
            self.assertIn("INFO", output)
        finally:
            self.logger_manager.remove_handler(handler)

    def test_proxy_preserves_arguments(self):
        """Test that logger proxy correctly passes through arguments"""
        # This test verifies that args and kwargs are properly forwarded
        import io

        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)

        self.logger_manager.add_handler(handler)

        try:
            # Log with formatting
            bot_logger.info("Value: %s", "test_value")
            output = stream.getvalue()
            self.assertIn("Value: test_value", output)
        finally:
            self.logger_manager.remove_handler(handler)


class TestImportConsistency(unittest.TestCase):
    """Test that different import styles access the same logger"""

    def test_bot_interface_logger_import(self):
        """Test importing logger from bot_interface"""
        from bot_interface import logger
        self.assertIsNotNone(logger)
        self.assertTrue(hasattr(logger, 'debug'))

    def test_emotion_analyze_logger(self):
        """Test logger in emotion_analyze module"""
        from emotion_analyze import logger
        self.assertIsNotNone(logger)

    def test_emotion_analyze_v2_logger(self):
        """Test logger in emotion_analyze_v2 module"""
        from emotion_analyze_v2 import logger
        self.assertIsNotNone(logger)

    def test_vista_manager_logger(self):
        """Test logger in maica_vista_files_manager module"""
        from maica_vista_files_manager import logger
        self.assertIsNotNone(logger)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
