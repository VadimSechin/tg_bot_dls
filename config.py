from enum import Enum

token = '5233839078:AAFczBS7Q_ftYPe6irtsmX9TNc1JbCf4ErI'
db_file = "database.vdb"


class States(Enum):
    """
    Мы используем БД Vedis, в которой хранимые значения всегда строки,
    поэтому и тут будем использовать тоже строки (str)
    """
    S_START = "0"  # Начало нового диалога
    S_SEND_PIC = "1"
    S_SEND_STYLE = "2"
    S_PROCESSING = "3"