from loguru import logger
from datetime import datetime
import sys

current_data_and_time = datetime.now().strftime('%H-%M_%d-%m-%y')

log_format = '<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{module}:{line}</cyan> | <level>{message}</level>'

logger.remove()

logger.add(sink=f'./user_data/logs/{current_data_and_time}.log', format=log_format, enqueue=True)

logger.add(sink=sys.stdout, format=log_format, enqueue=True)