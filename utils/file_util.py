import base64
import logging
import logging.config as config
from logging.handlers import TimedRotatingFileHandler
from pythonjsonlogger.jsonlogger import JsonFormatter
import sys

import logging
import logging.config
import os, shutil
from typing import List

def get_env_key_val(name: str, default: bool):
    return os.getenv(name) if os.getenv(name) else default

class YamlDict2Mem(dict):
    def __getattr__(self, name):
        value = self[name]
        if isinstance(value, dict):
            value = YamlDict2Mem(value)
        return value

stdout_loglvl = get_env_key_val("STDOUT_LOG_LEVEL", logging.WARNING)
if not stdout_loglvl in logging._nameToLevel:
    stdout_loglvl = logging.DEBUG

print("Setting stdout loglvl to {}".format(stdout_loglvl))
file_loglvl = get_env_key_val("FILE_LOG_LEVEL", logging.DEBUG)
if not file_loglvl in logging._nameToLevel:
    file_loglvl = logging.DEBUG
print("Setting file loglvl to {}".format(file_loglvl))

base_directory = "logs"
dirname = os.path.dirname(os.path.abspath(__file__))
parent_folder_name = dirname.split('/')[-1] 
APP_NAME = parent_folder_name
APP_VERSION = "0.1"

if not os.path.exists(base_directory):
    os.makedirs(base_directory)

def detect_file(path: str):
    if len(path.split('.')) > 1 : 
        return True
    return False

def detect_folder(path: str):
    if len(path.split('.')) == 1 : 
        return True
    return False

def clear_up(paths: List[str], logger=None):
    if not logger: 
        logger = get_logger("Cleanup")

    for path in paths: 
        logger.info("Checking path: " + path)
        if os.path.exists(path):
            if detect_folder(path) :
                logger.warning("Removing " + path) 
                shutil.rmtree(path)
            elif detect_file(path) : 
                logger.warning("Removing " + path)
                os.remove(path)



def get_logger(name: str, add_stdout=True, add_file=True, default_log_level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(stdout_loglvl)

    fmt = logging.Formatter('%(name)s | %(levelname)s  | %(asctime)s ｜ %(filename)s ｜ %(funcName)s ｜ %(lineno)s ｜ %(message)s')
    json_fmt = JsonFormatter('%(levelname)s %(message)s %(asctime)s %(name)s %(funcName)s %(lineno)d %(thread)d %(pathname)s', json_ensure_ascii=False)


    if add_stdout:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(stdout_loglvl)
        stream_handler.setFormatter(fmt)
        logger.addHandler(stream_handler)

    if add_file:
        # file_handler = logging.FileHandler(f"./logs_{name}.txt", encoding='utf-8')
        file_handler = TimedRotatingFileHandler(os.path.join(base_directory ,f"./logs_{name}.json"), when='d', interval=1, backupCount=60)
        file_handler.setLevel(file_loglvl)
        file_handler.setFormatter(json_fmt)
        logger.addHandler(file_handler)

    if not add_stdout and not add_file: 
        print("You should at least set one of the handlers to True")
        sys.exit(0)

    return logger