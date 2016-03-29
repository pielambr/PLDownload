import youtube_dl, os
from multiprocessing.pool import ThreadPool
from youtube_dl.utils import DownloadError
from datetime import datetime
from uuid import uuid4


class Download:
    link = ""
    done = False
    error = False
    started = None
    uuid = ""
    total = 0
    finished = 0
    title = ""

    def __init__(self, link):
        self.link = link
        self.started = datetime.now()
        self.uuid = str(uuid4())

    def download(self):
        curr_path = os.path.dirname(os.path.abspath(__file__))
        output_path = curr_path + "/downloads/" + self.uuid + "/%(title)s-%(id)s.%(ext)s"
        try:
            youtube_dl._real_main(["--yes-playlist", "-R", "10", "-x", "--audio-format", "mp3",
                                   "--output", output_path,
                                   "--restrict-filenames", "-v", self.link])
        except DownloadError:
            self.error = True
        finally:
            self.done = True

    def start(self):
            pool = ThreadPool()
            pool.apply_async(self.download)
