import uuid
import time


class Common:

    def gen_rnd_filename():
        """
        Returns a random file name
        """
        return str(uuid.uuid4())

    def getCurrentTimeMil():
        """
        returns current time in MilliSeconds
        """
        return int(round(time.time() * 1000))