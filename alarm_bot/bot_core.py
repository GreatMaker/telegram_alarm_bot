import telegram
from telegram.error import NetworkError, Unauthorized
import threading
import logging
from time import sleep, time
from alarm_bot import db
from alarm_bot.config import *
import subprocess

# create logger
module_logger = logging.getLogger(__name__)


class Bot(threading.Thread):
    run_flag = True
    config = None
    bot = None
    bot_name = None
    lock = None

    def __init__(self, config_obj):
        threading.Thread.__init__(self)
        self.thread_name = 'Bot'
        self.bot_name = None
        self.config = config_obj
        self.q = workQueue

    def kill_thread(self):
        self.run_flag = False

    def run(self):
        module_logger.debug('Starting ' + self.thread_name)

        # Telegram Bot Authorization Token
        self.bot = telegram.Bot(self.config.get('bot', 'token'))

        # Save bot name (this is the name given to BotFather for this token)
        self.bot_name = self.bot.get_me().first_name

        # get the first pending update_id, this is so we can skip over it in case
        # we get an "Unauthorized" exception.
        try:
            update_id = self.bot.getUpdates()[0].update_id
        except IndexError:
            update_id = None

        while self.run_flag:
            try:
                update_id = self.serve(update_id)
            except NetworkError:
                sleep(0.2)
            except Unauthorized:
                # The user has removed or blocked the bot.
                update_id += 1

            # Check messages from queue
            if not self.q.empty():
                data = self.q.get()
                module_logger.debug('Data into queue')
                self.broadcast_cmd(data)

                self.q.task_done()

    def serve(self, update_id):
        for update in self.bot.getUpdates(offset=update_id, timeout=10):
            update_id = update.update_id + 1

            chat_id = update.message.chat_id
            message = update.message.text

            # lowercase and prepare cmd message only if text is present
            if update.message.text:
                cmd_message = update.message.text.lower()

            module_logger.debug('%d:%.3f:%s' % (chat_id, time(), message.replace('\n', ' ')))

            if chat_id < 0:
                continue  # bot should not be in a group

            # Detect commands
            if message.startswith('/'):
                command = cmd_message[1:]
                if command in ("start", "help"):
                    self.start_cmd(update)

                    # Save message to database
                    my_db = db.DBConnection()
                    my_db.insert_user(chat_id)
                elif command in ("ups", "apc"):
                    self.ups_cmd(update)
                elif command in ("raid", "disk"):
                    self.raid_cmd(update)
                else:
                    self.bot.sendMessage(chat_id=chat_id, text='Invalid command!')
                continue

        return update_id

    def start_cmd(self, update):
        self.bot.sendMessage(chat_id=update.message.chat_id, text=self.config.get('bot', 'start_msg'))

    def broadcast_cmd(self, message):
        my_db = db.DBConnection()
        users = my_db.select_users()

        for user in users:
            self.bot.sendMessage(chat_id=user[0], text=message)

    def ups_cmd(self, update):
        ret = subprocess.run(["apcaccess"], check=True, stdout=subprocess.PIPE, universal_newlines=True)
        self.bot.sendMessage(chat_id=update.message.chat_id, text=ret.stdout)

    def raid_cmd(self, update):
        ret = subprocess.run(["mdadm", "-D", "/dev/md0"], check=True, stdout=subprocess.PIPE, universal_newlines=True)
        self.bot.sendMessage(chat_id=update.message.chat_id, text=ret.stdout)