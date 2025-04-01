class HistoryMarker:
    def __init__(self, sprite, time_to_live):
        self._sprite = sprite
        self._time_to_live = time_to_live

    @property
    def sprite(self):
        return self._sprite

    @sprite.setter
    def sprite(self, new_sprite):
        self._sprite = new_sprite

    @property
    def time_to_live(self):
        return self._time_to_live

    @time_to_live.setter
    def time_to_live(self, value):
        self._time_to_live = value