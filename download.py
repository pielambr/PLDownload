import os
from datetime import datetime, timedelta
from shutil import rmtree
from uuid import uuid4
from zipfile import ZipFile

from youtube_dl import YoutubeDL

from update import DownloadUpdate, PlaylistUpdate, ZipUpdate


class Download:

    completed = False
    error = False
    zipped = False
    zipping = False
    total_completed = 0

    def __init__(self, session_id, link, hook):
        self.link = link
        self.session_id = session_id
        self.started = datetime.now()
        self.playlist_id = str(uuid4())
        self.hook = hook
        self.file_path = os.path.dirname(os.path.abspath(__file__)) + '/downloads/' + self.playlist_id

    def __call__(self, info):
        completed = info['status'] == 'finished'
        progress = int((info['downloaded_bytes'] / info['total_bytes']) * 100)
        if completed:
            self.total_completed += 1
        filename = info['filename'].split("/")[-1].replace(".m4a", ".mp3").replace(".webm", ".mp3")
        update = DownloadUpdate(self.playlist_id, progress, completed, self.total_completed, filename)
        self.hook(self.session_id, update)

    def get_files(self):
        if os.path.isdir(self.file_path):
            return {f: "download/" + self.playlist_id + "/" + f for f in os.listdir(self.file_path)
                    if (os.path.isfile(os.path.join(self.file_path, f)) and f.endswith(".mp3"))}
        else:
            return None

    def remove(self):
        if (self.completed or self.error) and (datetime.now() > self.started + timedelta(hours=1)):
            rmtree(self.file_path, True)
            return True
        return False

    def zip(self):
        if not self.zipping and not self.zipped and self.completed:
            self.zipping = True
            with ZipFile(self.file_path + "/playlist.zip", "w") as playlist_zip:
                for f in os.listdir(self.file_path):
                    if os.path.isfile(os.path.join(self.file_path, f)) and f.endswith(".mp3"):
                        playlist_zip.write(os.path.join(self.file_path, f), f)
                playlist_zip.close()
            self.zipping = False
            self.zipped = True
            self.hook(self.session_id, ZipUpdate(self.playlist_id))

    def start(self):
        curr_path = os.path.dirname(os.path.abspath(__file__))
        output_tmpl = curr_path + '/downloads/' + self.playlist_id + '/%(title)s-%(id)s.%(ext)s'
        options = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '3',
            }],
            'socket_timeout': '15',
            'progress_hooks': [self],
            'ignoreerrors': True,
            'outtmpl': output_tmpl,
        }
        ydl = YoutubeDL(options)
        return_code = ydl.download([self.link])
        self.completed = True
        self.error = return_code != 0
        update = PlaylistUpdate(self.playlist_id, playlist_error=self.error,
                                total_completed=self.total_completed)
        self.hook(self.session_id, update)

