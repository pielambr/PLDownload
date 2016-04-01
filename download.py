import json
import os
from datetime import datetime, timedelta
from shutil import rmtree
from uuid import uuid4

from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError


class Download:
    link = ""
    session_id = ""
    done = False
    error = False
    started = None
    playlist_id = ""
    total = 0
    finished = 0
    title = ""
    hook = None

    def __init__(self, session_id, link, hook):
        self.link = link
        self.session_id = session_id
        self.started = datetime.now()
        self.playlist_id = str(uuid4())
        self.hook = hook

    def __call__(self, info):
        finished = info['status'] == 'finished'
        progress = info['downloaded_bytes'] / info['total_bytes']
        if finished:
            self.finished += 1
        filename = info['filename'].split("/")[-1].replace(".m4a", ".mp3")
        update = DownloadUpdate(progress, filename, self.playlist_id, finished)
        self.hook(self.session_id, update)

    def get_files(self):
        file_path = os.path.dirname(os.path.abspath(__file__)) + '/downloads/' + self.playlist_id
        if os.path.isdir(file_path):
            return {f: "download/" + self.playlist_id + "/" + f for f in os.listdir(file_path)
                    if (os.path.isfile(os.path.join(file_path, f)) and f.endswith(".mp3"))}
        else:
            return None

    def remove(self):
        if (self.done or self.error) and (datetime.now() > self.started + timedelta(hours=1)):
            curr_path = os.path.dirname(os.path.abspath(__file__))
            rm_dir = curr_path + '/downloads/' + self.playlist_id
            rmtree(rm_dir, True)
            return True
        return False

    def start(self):
        curr_path = os.path.dirname(os.path.abspath(__file__))
        output_tmpl = curr_path + '/downloads/' + self.playlist_id + '/%(title)s-%(id)s.%(ext)s'
        try:
            options = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0',
                }],
                'socket_timeout': '15',
                'progress_hooks': [self],
                'outtmpl': output_tmpl,
            }
            ydl = YoutubeDL(options)
            ydl.download([self.link])
        except DownloadError:
            self.error = True
        finally:
            self.done = True


class DownloadUpdate:

    progress = 0
    playlist_id = ""
    filename = ""
    download_url = ""
    finished = False

    def __init__(self, progress, filename, playlist_id, finished):
        self.progress = progress
        self.filename = filename
        self.playlist_id = playlist_id
        self.finished = finished

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
