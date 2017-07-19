import logging
import threading
import time

from lib.api.screenrecord import ScreenRecord
from lib.common.abstracts import Auxiliary
from lib.common.results import NetlogFile

log = logging.getLogger(__name__)

class ScreenRecorder(threading.Thread, Auxiliary):
    """Record screen for a whole analysis"""

    def __init__(self, options={}, analyzer=None):
        threading.Thread.__init__(self)
        Auxiliary.__init__(self, options, analyzer)
        self.src = ScreenRecord()

    def stop(self):
        """Stop screenrecording"""
        with open(self.src.output, "rb") as f:
            nf = NetlogFile()
            nf.init("shots/" + self.src.filename)
            nf.sock.sendall(f.read())
            nf.close()

    def start(self):
        """Run screenrecording"""
        self.src.record()
