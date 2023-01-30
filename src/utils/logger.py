import sys
import logging
import logging.handlers

# Logger setup 
def setup_logger(name='discord') -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')

    file_handler = logging.handlers.RotatingFileHandler(
        filename='log/discord.log',
        encoding='utf-8',
        maxBytes=4 * 1024 * 1024,  # 1 MiB
        backupCount=5,  # Rotate through 5 files
    )
    file_handler.setFormatter(formatter)

    console_handler = (logging.StreamHandler(sys.stdout)) # Mirror logs to stdout for journalctl to catch and for debugging
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger