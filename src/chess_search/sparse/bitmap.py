from pyroaring import BitMap
from chess_search.utils import position_to_tokens


class BitmapIndex:
    def __init__(self):
        self.index = {}

    def add(self, position_id, board):
        for token in position_to_tokens(board):
            if token not in self.index:
                self.index[token] = BitMap()
            self.index[token].add(position_id)

    def __ior__(self, other):
        for token, bitmap in other.index.items():
            if token in self.index:
                self.index[token] |= bitmap
            else:
                self.index[token] = bitmap.copy()
        return self

    def __len__(self):
        return len(self.index)