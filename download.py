import json

import os
from youtube_dl import YoutubeDL
from multiprocessing.pool import ThreadPool
from youtube_dl.utils import DownloadError
from datetime import datetime
from uuid import uuid4


class Download:
    link = ""
    session_id = ""
    done = False
    error = False
    started = None
    uuid = ""
    total = 0
    finished = 0
    title = ""
    ydl = None
    hook = None

    def __init__(self, session_id, link, hook):
        self.link = link
        self.session_id = session_id
        self.started = datetime.now()
        self.uuid = str(uuid4())
        self.hook = hook

    def __call__(self, info):
        finished = info['status'] == 'finished'
        progress = info['downloaded_bytes'] / info['total_bytes']
        if finished:
            self.finished += 1
        filename = info['filename'].split("/")[-1].replace(".m4a", ".mp3")
        download = "download/" + self.uuid + "/" + filename
        update = DownloadUpdate(progress, filename, finished, download)
        self.hook(self.session_id, update)

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
        if os.path.isdir(file_path):
            return {f: "download/" + self.uuid + "/" + f for f in os.listdir(file_path)
                    if (os.path.isfile(os.path.join(file_path, f)) and f.endswith(".mp3"))}
        else:
            return None

    def start(self):
        pool = ThreadPool()
        pool.apply_async(self.download)


class DownloadUpdate:

    progress = 0
    filename = ""
    download_url = ""
    finished = False

    def __init__(self, progress, filename, finished, download_url):
        self.progress = progress
        self.filename = filename
        if finished:
            progress = 1
            finished = True
            self.download_url = download_url

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)