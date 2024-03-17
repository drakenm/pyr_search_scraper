import logging, sys
class Log_Init:

    @classmethod
    def __init__(cls, logger_name:str, app_log_path:str) -> None:
        #need to make sure we are sending args and if not raise an exception, look for env logger and log path
        if logger_name not in logging.Logger.manager.loggerDict: # setup the app logger once
            logger = logging.getLogger( logger_name )
            logger.setLevel(logging.DEBUG)
            logger_fh = logging.FileHandler( app_log_path, mode='w', encoding='utf-8' )
            logger_fh.setLevel( logging.DEBUG )
            logger_ch = logging.StreamHandler(sys.stdout)
            logger_ch.setLevel( logging.ERROR )
            logger_formatter = logging.Formatter( '%(name)s\\%(levelname)s[%(asctime)s]: %(message)s' )
            logger_fh.setFormatter( logger_formatter )
            logger_ch.setFormatter( logger_formatter )
            logger.addHandler( logger_fh )
            logger.addHandler( logger_ch )
            cls.logger = logger
    
    @classmethod
    def getLogger(cls) -> logging.Logger:
        return cls.logger