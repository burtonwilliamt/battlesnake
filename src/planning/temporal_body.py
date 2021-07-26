import queue
from typing import Iterable

import src.models as models


class TemporalBody:

    def __init__(self, body: Iterable[models.Coord]):
        self.current_body = list(body)
        self.old_tails = queue.deque()

    def __len__(self):
        return len(self.current_body)

    def __iter__(self):
        return iter(self.current_body)

    def head(self) -> models.Coord:
        return self.current_body[0]

    def tail(self) -> models.Coord:
        return self.current_body[-1]

    def add_head(self, loc: models.Coord):
        self.current_body.insert(0, loc)

    def undo_add_head(self):
        self.current_body.pop(0)

    def del_tail(self):
        self.old_tails.append(self.current_body.pop())

    def undo_del_tail(self):
        self.current_body.append(self.old_tails.pop())

    def grow(self):
        self.current_body.append(self.tail())

    def undo_grow(self):
        self.current_body.pop()

