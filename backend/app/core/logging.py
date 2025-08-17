import logging

logger = logging.getLogger("manim_app")
logger.setLevel(logging.INFO)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s - %(message)s")
ch.setFormatter(formatter)

logger.addHandler(ch)
