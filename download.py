import os, youtube_dl
from youtube_dl import YoutubeDL
from multiprocessing.pool import ThreadPool
from youtube_dl.utils import DownloadError
from datetime import datetime
from uuid import uuid4


class Download:
    link = ''
    done = False
    error = False
    started = None
    uuid = ''
    total = 0
    finished = 0
    title = ''
    ydl = None

    def __init__(self, link):
        self.link = link
        self.started = datetime.now()
        self.uuid = str(uuid4())

    def __call__(self, info):
        if info['status'] == 'finished':
            self.finished += 1
        print("\n \n INFO: " + str(info) + "\n")

    def download(self):
        curr_path = os.path.dirname(os.path.abspath(__file__))
        output_tmpl = curr_path + '/downloads/' + self.uuid + '/%(title)s-%(id)s.%(ext)s'
        try:
            options = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '5',
                }],
                'progress_hooks': [self],
                'outtmpl': output_tmpl,
            }
            self.ydl = YoutubeDL(options)
            self.ydl.download([self.link])
        except DownloadError:
            self.error = True
        finally:
            self.done = True

    def get_files(self):
        file_path = os.path.dirname(os.path.abspath(__file__)) + '/downloads/' + self.uuid
        return [f for f in os.listdir(file_path) if os.isfile(os.join(file_path, f))]

    def start(self):
            pool = ThreadPool()
            pool.apply_async(self.download)
