import logging
import threading
import time
import os

from lib.api.screenrecord import ScreenRecord
from lib.common.abstracts import Auxiliary
from lib.common.results import NetlogFile

log = logging.getLogger(__name__)

class ScreenRecorder(threading.Thread, Auxiliary):
    """Record screen for a whole analysis"""

    def __init__(self, options={}, analyzer=None):
        threading.Thread.__init__(self)
        Auxiliary.__init__(self, options, analyzer)
        self.file_name = "test.mp4"
        self.src = ScreenRecord(os.environ["TEMP"], self.file_name)

    def stop(self):
        """Stop screenrecording"""
        # Stop the video
        self.src.stop()

        # TODO: taking video based on events
        try:
            with open(self.src.output, "rb") as f:
                nf = NetlogFile()
                nf.init("screenrecord/%s" % self.src.filename)
                nf.sock.sendall(f.read())
                nf.close()
        except Exception as e:
            log.debug("Screenrecord bug: %s", e);

    def start(self):
        """Run screenrecording"""
        self.src.record()
