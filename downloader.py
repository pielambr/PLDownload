from download import Download


class Downloader:

    downloads = {}

    def add_download(self, session, link):
        download = Download(link)
        if session not in self.downloads:
            self.downloads[session] = []
        self.downloads[session].append(download)
        download.start()

    def get_downloads(self, session):
        try:
            return self.downloads[session]
        except KeyError:
            return None
