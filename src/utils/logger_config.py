from loguru import logger
from datetime import datetime
import sys

# Generate a timestamp for the log file name.
current_data_and_time = datetime.now().strftime('%H-%M_%d-%m-%y')

# Define the log message format.
log_format = '<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <cyan>{module}:{line}</cyan> | <level>{message}</level>'

# Remove the default Loguru handler.
logger.remove()

# Add file-based logger with timestamped filename.
logger.add(sink=f'./user_data/logs/{current_data_and_time}.log', format=log_format, enqueue=True)

# Add console logger for real-time output.
logger.add(sink=sys.stdout, format=log_format, enqueue=True)
