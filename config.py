from enum import Enum

token = '5233839078:AAFczBS7Q_ftYPe6irtsmX9TNc1JbCf4ErI'
db_file = "database.vdb"


class States(Enum):
    S_START = "0"
    S_SEND_PIC = "1"
    S_SEND_STYLE = "2"
    S_PROCESSING = "3"

class IS_PROCESSING:
    def __init__(self):
        self.is_processing = False

    def __str__(self):
        return str(self.is_processing)

    def change(self, new_state):
        assert isinstance(new_state,bool)
        self.is_processing = new_state

is_processing = IS_PROCESSING()