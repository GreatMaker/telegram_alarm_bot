import signal
from alarm_bot import bot_core
from alarm_bot import monitor
from multiprocessing import Queue
import threading
import logging
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import argparse

# Logging init and level
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--config", help="Bot config file", required=True)  # mandatory config file as parameter
args = vars(parser.parse_args())

# Read config file
config = configparser.ConfigParser()
config.read(args['config'])

threads = []


def signal_handler(signal, frame):
    for t in threads:
        t.kill_thread()


def main():
    # Allocate and start bot class using token from config file
    bot_thread = bot_core.Bot(config)
    bot_thread.start()

    monitor_thread = monitor.Monitor(config)
    monitor_thread.start()

    # Append threads
    threads.append(bot_thread)
    threads.append(monitor_thread)

    # signal for sigint
    signal.signal(signal.SIGINT, signal_handler)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    logger.debug('Exiting Main Thread')


if __name__ == '__main__':
    main()
