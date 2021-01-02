import logging

output = "."

logger = logging.getLogger("Program Name-Version")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

consoleHeader = logging.StreamHandler()
consoleHeader.setFormatter(formatter)
consoleHeader.setLevel(logging.INFO)

fileHandler = logging.FileHandler(f"{output}/output.log")
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)

logger.addHandler(fileHandler)
logger.addHandler(consoleHeader)


def wrap(pre, post):
    """ Wrapper """

    def decorate(func):
        """ Decorator """

        def call(*args, **kwargs):
            """ Actual wrapping """
            # Note: maybe pre(func, *args, **kwargs) in order to log arguments?
            pre(func)
            result = func(*args, **kwargs)
            post(func)
            return result

        return call

    return decorate


def entering(func, *args, **kwargs):
    """ Pre function logging """
    logger.info("Entered %s", func.__name__)
    logger.debug(func.__doc__)
    logger.debug(
        "Function at line %d in %s"
        % (func.__code__.co_firstlineno, func.__code__.co_filename)
    )
    try:
        logger.debug("Function argument: %s" % (func.__code__.co_varnames[0]))
    except:
        logger.debug("No arguments")


def exiting(func):
    """ Post function logging """
    logger.info("Exited  %s", func.__name__)
