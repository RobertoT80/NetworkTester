import os, sys, platform
import logging
from logging import handlers

class Log(object):
    def __init__(self, logname):
        self.logger = logging.getLogger(logname)
        self.logger.setLevel(logging.DEBUG)
        self.logname = logname
        self.user_path = os.getenv('USERPROFILE')
        # file handler
        if not len(self.logger.handlers):
            if sys.platform == 'darwin':
                self.ini_path = os.path.join(os.path.expanduser("~"), 'Library', 'Application Support', logname)
            elif platform.release() == 'XP': 
                self.ini_path = os.path.join(self.user_path, 'Application Data', logname)
            elif (platform.release() == "7") or ('2008' in platform.release()) or ('2012' in platform.release()): 
                self.ini_path = os.path.join(self.user_path, 'Appdata', 'Roaming', logname)
            if not os.path.exists(self.ini_path):
                try:
                    os.mkdir(self.ini_path)
                except OSError as err:
                    print(err)
            self.log_path = os.path.join(self.ini_path, 'Log')
            if not os.path.exists(self.log_path):
                print('creating dirs')
                try:
                    os.mkdir(self.log_path)
                except OSError as err:
                    print("Can't create log dir: {0}, {1}.\nExiting...".format(self.log_path, err))
                    raise SystemExit(err)
            if len(self.log_path) > 0:
                self.logfile = os.path.join(self.log_path, '{0}.{1}.{2}.log'.format(
                    self.logname, platform.node(), self.user_path.split('\\')[-1]))
                #logging_handler = logging.FileHandler(self.logfile)
                logging_handler = handlers.RotatingFileHandler(self.logfile, maxBytes=262144, backupCount=5)
                logging_handler.setLevel(logging.DEBUG)
                # logging format
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                logging_handler.setFormatter(formatter)
                # handlers
                self.logger.addHandler(logging_handler)

    def __str__(self):
        return 'log: ' + "({}) ".format(self.logname) + self.get_attr('logfile')

    def get_attr(self, arg):
        """
        get_attr('logpath') >
        get_attr('logfile') >
        """
        if not arg:
            pass
        else:
            if arg == 'log_path':
                return self.__dict__['log_path']
            elif arg == 'logfile':
                return self.__dict__['logfile']
            elif arg == 'ini_path':
                return self.__dict__['ini_path']

