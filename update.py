from json import dumps


class JsonUpdate:

    def json(self):
        return dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class DownloadUpdate(JsonUpdate):

    type = "download_update"

    def __init__(self, playlist_id, file_progress=0, file_completed=False, total_completed=0, current_filename=""):
        self.playlist_id = playlist_id
        self.file_progress = file_progress
        self.file_completed = file_completed
        self.total_completed = total_completed
        self.current_filename = current_filename


class PlaylistUpdate(JsonUpdate):

    type = "playlist_update"

    def __init__(self, playlist_id, playlist_completed=True, playlist_error=False, total_completed=0):
        self.playlist_id = playlist_id
        self.playlist_completed = playlist_completed
        self.total_completed = total_completed
        self.playlist_error = playlist_error


class ZipUpdate(JsonUpdate):

    type = "zip_update"

    def __init__(self, playlist_id):
        self.finished = True
        self.playlist_id = playlist_id
