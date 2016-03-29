from download import Download


class Downloader:

    downloads = []

    def add_download(self, link):
        download = Download(link)
        self.downloads.append(download)
