__title__ = 'easytello'
__author__ = 'Ezra Fielding'
__liscence__ = 'MIT'
__copyright__ = 'Copyright 2019 Ezra Fielding'
__version__ = '0.0.7'
__all__ = ['tello', 'command_log', 'command', 'error']

from .tello import Tello, BaseTello, CommandLoggerMixin, SocketManagerMixin
from .command_log import CommandLog
