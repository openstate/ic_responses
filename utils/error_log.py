
from settings import ERROR_LOG_NAME

class ErrorLog(object):
  def __new__(cls):
    if not hasattr(cls, 'instance'):
      cls.instance = super(ErrorLog, cls).__new__(cls)
    return cls.instance

  def __init__(self):
    self.error_file = open(ERROR_LOG_NAME, 'a')

  def write(self, error):
    self.error_file.write(f"\n{error}\n")
    self.error_file.flush()