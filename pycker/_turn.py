import datetime


class Turn(object):
    @property
    def time(self):
        return self._time

    @property
    def elapsed(self):
        return datetime.datetime.now() - self._time

    @property
    def session(self):
        return self._session

    def __init__(self, session):
        self._time = None
        self._session = session

    def __enter__(self):
        self._time = datetime.datetime.now()
        self._start_mouse_pos = self.session.mouse.position()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.mouse.move(*self._start_mouse_pos)
