from iobot import IOBot

preset_videos = {
    "pikachu": "https://www.youtube.com/watch?v=7aVcisdS8X0",
    "boris": "https://www.youtube.com/watch?v=b18DjXWyWuc"
}

class IOBotVideo(IOBot):

    def __init__(self, preset_videos=preset_videos):
        super(IOBotVideo, self).__init__()
        self._preset_videos = {}
        self.preset_videos = preset_videos

    @property
    def preset_videos(self):
        return self._preset_videos

    @preset_videos.setter
    def preset_videos(self, dict_entry):
        if isinstance(dict_entry, dict):
            self._preset_videos.update(dict_entry)

    def video(self, query):
        return self._preset_videos[query]