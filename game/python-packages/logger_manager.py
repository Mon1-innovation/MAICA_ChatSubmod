# -*- coding: utf-8 -*-
"""
Logger Manager - Centralized logger configuration and synchronization

This module provides a singleton LoggerManager that enables runtime logger
modifications with automatic synchronization to all referenced points.

Key Features:
- Singleton pattern for centralized management
- Dynamic logger retrieval to always get latest configuration
- Injection point registry for automatic synchronization
- Support for multiple logger wrappers
- Compatible with .rpy file dynamic assignments
"""

import logging
import sys


class LoggerManager(object):
    """
    Singleton manager for logger configuration and synchronization.

    Manages:
    - Root logger instance and handlers
    - Formatter configuration
    - Injection points registry for automatic synchronization
    - Runtime modifications with sync propagation
    """

    _instance = None
    _initialized = False
    _fallback_logger_name = "maica_logger_manager"
    _fallback_handler_marker = "_maica_logger_manager_handler"

    def __new__(cls):
        """Ensure singleton pattern"""
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize LoggerManager (only on first instantiation)"""
        if LoggerManager._initialized:
            return

        LoggerManager._initialized = True

        # Keep the standalone fallback isolated from the process-wide root logger.
        # MAS supplies its own logging hierarchy, so attaching a handler to the
        # real root would make MAS loggers emit duplicate records after injection.
        self._root_logger = logging.getLogger(self._fallback_logger_name)
        self._root_logger.setLevel(logging.DEBUG)
        self._root_logger.propagate = False

        # Reuse the manager-owned handler across module reloads.
        self._stream_handler = None
        for handler in list(self._root_logger.handlers):
            if getattr(handler, self._fallback_handler_marker, False):
                self._stream_handler = handler
                break

        if self._stream_handler is None:
            self._stream_handler = logging.StreamHandler(sys.stdout)
            setattr(self._stream_handler, self._fallback_handler_marker, True)
            self._root_logger.addHandler(self._stream_handler)

        self._stream_handler.setLevel(logging.DEBUG)

        # Create formatter
        self._formatter = logging.Formatter(
            fmt="%(asctime)s:%(levelname)s:%(message)s",
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self._stream_handler.setFormatter(self._formatter)

        # Registry for injection points that need synchronization
        # Format: {name: (module, attribute_name, current_logger_ref)}
        self._injected_references = {}

    @property
    def logger(self):
        """Get the current root logger instance"""
        return self._root_logger

    def set_logger(self, new_logger):
        """
        Replace the root logger with a custom logger instance.

        This is useful for integrating with external logging systems (e.g., RenPy's submod_log).
        After replacing the logger, all module loggers will automatically use the new logger
        through their dynamic proxy mechanisms.

        Args:
            new_logger: A logger-like object with debug, info, warning, error, critical methods
        """
        if new_logger is None:
            if self._root_logger:
                self._root_logger.warning("Attempt to set logger to None, operation ignored")
            return

        self._root_logger = new_logger

        # NOTE: We do NOT call _sync_injected_references() here because:
        # - All module loggers (bot_interface.logger, emotion_analyze_v2.logger, etc.)
        #   use dynamic proxies that retrieve the logger on each call
        # - They will automatically use the new logger without needing synchronization

    def set_log_level(self, level):
        """
        Set the log level for all handlers and the root logger.

        Args:
            level: logging level (e.g., logging.DEBUG, logging.INFO, etc.)
        """
        set_level = getattr(self._root_logger, "setLevel", None)
        if callable(set_level):
            set_level(level)
        elif hasattr(self._root_logger, "level"):
            self._root_logger.level = level
        self._stream_handler.setLevel(level)
        self._sync_injected_references()

    def add_handler(self, handler):
        """
        Add a new handler to the logger.

        Args:
            handler: logging.Handler instance
        """
        add_handler = getattr(self._root_logger, "addHandler", None)
        if not callable(add_handler):
            self._root_logger.warning("Current logger does not support handlers")
            return
        add_handler(handler)
        self._sync_injected_references()

    def remove_handler(self, handler):
        """
        Remove a handler from the logger.

        Args:
            handler: logging.Handler instance
        """
        remove_handler = getattr(self._root_logger, "removeHandler", None)
        if not callable(remove_handler):
            self._root_logger.warning("Current logger does not support handlers")
            return
        remove_handler(handler)
        self._sync_injected_references()

    def set_formatter(self, fmt=None, datefmt=None):
        """
        Set formatter for the stream handler.

        Args:
            fmt: Format string (default: "%(asctime)s:%(levelname)s:%(message)s")
            datefmt: Date format string (default: '%Y-%m-%d %H:%M:%S')
        """
        if fmt is None:
            fmt = "%(asctime)s:%(levelname)s:%(message)s"
        if datefmt is None:
            datefmt = '%Y-%m-%d %H:%M:%S'

        self._formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
        self._stream_handler.setFormatter(self._formatter)
        self._sync_injected_references()

    def register_injected_reference(self, name, module, attr_name):
        """
        Register an injection point for tracking and synchronization.

        Args:
            name: Unique name for this injection point
            module: Module object containing the injected attribute
            attr_name: Attribute name in the module (e.g., 'logger', 'default_logger')
        """
        self._injected_references[name] = {
            'module': module,
            'attr_name': attr_name,
            'current_logger': getattr(module, attr_name, None)
        }
        self._root_logger.debug("Registered injection point: {}".format(name))

    def _sync_injected_references(self):
        """
        Synchronize all registered injection points with current logger state.

        This is called automatically after configuration changes to ensure
        all modules get the latest logger configuration.
        """
        root_level = getattr(self._root_logger, 'level', None)
        for name, ref_info in self._injected_references.items():
            try:
                module = ref_info['module']
                attr_name = ref_info['attr_name']

                # Get current logger from module
                current_logger = getattr(module, attr_name, None)

                # Dynamic proxies already resolve the current logger on every call.
                # For distinct stdlib loggers, synchronize only the level. Copying
                # handlers here causes each record to be handled by both the child
                # and its parent when propagation remains enabled.
                if (
                    isinstance(current_logger, logging.Logger)
                    and current_logger is not self._root_logger
                    and isinstance(self._root_logger, logging.Logger)
                ):
                    if root_level is not None:
                        current_logger.setLevel(root_level)

                self._root_logger.debug("Synced injection point: {}".format(name))
            except Exception as e:
                self._root_logger.error(
                    "Failed to sync injection point {}: {}".format(name, e)
                )

    def get_status(self):
        """
        Get current logger status as a dictionary.

        Returns:
            dict: Status information
        """
        handlers = list(getattr(self._root_logger, 'handlers', []))
        return {
            'logger_level': logging.getLevelName(getattr(self._root_logger, 'level', logging.NOTSET)),
            'handler_count': len(handlers),
            'handlers': [type(h).__name__ for h in handlers],
            'formatter': str(self._formatter._fmt) if self._formatter else None,
            'injected_references': list(self._injected_references.keys())
        }


class LoggerWrapper(object):
    """
    Wrapper for a single logger instance.

    Allows lazy retrieval of logger from LoggerManager,
    ensuring you always get the latest configuration.
    """

    def __init__(self, logger_manager=None):
        """
        Initialize LoggerWrapper.

        Args:
            logger_manager: LoggerManager instance (default: get_logger_manager())
        """
        if logger_manager is None:
            logger_manager = get_logger_manager()
        self._manager = logger_manager

    @property
    def logger(self):
        """Get current logger from manager"""
        return self._manager.logger

    def debug(self, msg, *args, **kwargs):
        """Log debug message"""
        return self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Log info message"""
        return self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Log warning message"""
        return self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Log error message"""
        return self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """Log critical message"""
        return self.logger.critical(msg, *args, **kwargs)

    def __getattr__(self, name):
        """Delegate unknown attributes to the wrapped logger"""
        return getattr(self.logger, name)


class MultiLoggerWrapper(object):
    """
    Wrapper for multiple logger instances.

    Allows delegating to multiple loggers simultaneously,
    useful for cases like logger_both that logs to multiple destinations.
    """

    def __init__(self, loggers=None):
        """
        Initialize MultiLoggerWrapper.

        Args:
            loggers: List of logger instances or LoggerWrapper instances
        """
        if loggers is None:
            loggers = []
        self._loggers = loggers

    def add_logger(self, logger):
        """Add a logger to the wrapper"""
        if logger not in self._loggers:
            self._loggers.append(logger)

    def remove_logger(self, logger):
        """Remove a logger from the wrapper"""
        if logger in self._loggers:
            self._loggers.remove(logger)

    def _call_all(self, method_name, *args, **kwargs):
        """Call method on all wrapped loggers"""
        for logger in self._loggers:
            if hasattr(logger, method_name):
                method = getattr(logger, method_name)
                if callable(method):
                    method(*args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Log debug message to all loggers"""
        self._call_all('debug', msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Log info message to all loggers"""
        self._call_all('info', msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Log warning message to all loggers"""
        self._call_all('warning', msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Log error message to all loggers"""
        self._call_all('error', msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """Log critical message to all loggers"""
        self._call_all('critical', msg, *args, **kwargs)

    def setLevel(self, level):
        """Set level on all loggers"""
        for logger in self._loggers:
            if hasattr(logger, 'setLevel'):
                logger.setLevel(level)


# Global singleton instance
_logger_manager = None


def get_logger_manager():
    """
    Get or create the global LoggerManager singleton.

    Returns:
        LoggerManager: The singleton instance
    """
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager


def get_logger():
    """
    Get the current logger from LoggerManager.

    This function should be used in modules that need the latest
    logger configuration. It ensures that runtime modifications
    are always reflected.

    Returns:
        logging.Logger: The root logger instance
    """
    return get_logger_manager().logger
