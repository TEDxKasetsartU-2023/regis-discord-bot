# log management
# | IMPORT
import os

from datetime import datetime

# | GLOBAL VARIABLES
DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3
CRITICAL = 4

# | Classes
class logger:
    LOG_LEVEL = {0: "debug", 1: "info", 2: "warning", 3: "error", 4: "critical"}
    def __init__(self, log_dir: str, date_format: str = "%Y%m%d%H%M%S", default_log_level: int = 1) -> None:
        self.date_format = date_format
        self.log_dir = os.path.abspath(log_dir)
        
        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)

        self.log_file_name = f"{self.get_timestamp()}_log.log"
        self.default_log_level = default_log_level

    def write_log(self, content: str, log_level: int) -> str:
        _log = self.get_log(content, log_level)
        with open(os.path.join(self.log_dir ,self.log_file_name), "at", encoding="utf-8") as f:
            f.write(_log + "\n")
        return _log

    def get_timestamp(self) -> str:
        return datetime.now().strftime(self.date_format)

    def print_log(self, content: str, log_level: int = None) -> None:
        if log_level is None:
            log_level = self.default_log_level
        _log = self.write_log(content, log_level)
        print(_log)

    def get_log(self, content: str, log_level: int) -> str:
        return f"{self.get_timestamp()} :: [{logger.LOG_LEVEL[log_level]:^8}] :: {content}"


# | MAIN
if __name__ == "__main__":
    l = logger()
    while True:
        i = input(">>> ")
        if i == "":
            break
        l.print_log(i)
