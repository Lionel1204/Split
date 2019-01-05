import os
import logging
from logging.handlers import RotatingFileHandler


class Logger(object):
    _filePath = r"./log/running.log"
    _logPath = r"./log/"

    def __init__(self):
        if not os.path.isdir(self._logPath):
            os.mkdir(self._logPath)

        formatter = logging.Formatter('%(asctime)-15s %(levelname)s [%(filename)s %(funcName)s] Line: %(lineno)d MSG: %(message)s')
        rh = RotatingFileHandler(self._filePath,
                                    maxBytes=100*1024*1024,
                                    backupCount=10
                                       )
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        rh.setFormatter(formatter)
        self.logger.addHandler(rh)