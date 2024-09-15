import logging

def setup_logging():
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)

    # Create file handler
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.ERROR)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
