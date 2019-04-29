import select
from systemd import journal
import threading
import pprint
import logging
from time import sleep
from alarm_bot.config import *

# create logger
module_logger = logging.getLogger(__name__)


class Monitor(threading.Thread):
    run_flag = True
    config = None
    lock = None
    j = None
    p = None

    def __init__(self, config_obj):
        threading.Thread.__init__(self)
        self.thread_name = 'Monitor'
        self.config = config_obj
        self.q = workQueue

    def kill_thread(self):
        self.run_flag = False

    def run(self):
        module_logger.debug('Starting ' + self.thread_name)

        # Create a systemd.journal.Reader instance with level
        self.j = journal.Reader()
        self.j.log_level(journal.LOG_INFO)

        # Only include entries since the current box has booted.
        self.j.this_boot()
        self.j.this_machine()

        # Filter log entries
        self.j.add_match(
            _SYSTEMD_UNIT=u'apcupsd.service'
        )

        # Move to the end of the journal
        self.j.seek_tail()

        # Important! - Discard old journal entries
        self.j.get_previous()

        # Create a poll object for journal entries
        self.p = select.poll()

        # Register the journal's file descriptor with the polling object.
        journal_fd = self.j.fileno()
        poll_event_mask = self.j.get_events()
        self.p.register(journal_fd, poll_event_mask)

        while self.run_flag:
            if self.p.poll(1000):
                if self.j.process() == journal.APPEND:
                    for entry in self.j:
                        msg_str = entry['_SYSTEMD_UNIT'] + ' - ' + entry['MESSAGE']
                        module_logger.debug(msg_str)
                        # pprint.pprint(entry)
            #            self.lock.acquire()
                        self.q.put(msg_str)
            #            self.lock.release()
