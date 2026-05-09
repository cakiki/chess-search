from pyroaring import BitMap
from chess_search.utils import position_to_tokens
import lmdb


class BitmapIndex:
    def __init__(self):
        self.index = {}

    def add(self, position_id, board):
        for token in position_to_tokens(board):
            if token not in self.index:
                self.index[token] = BitMap()
            self.index[token].add(position_id)

    def query(self, tokens):
        bitmaps = [self.index[t] for t in tokens if t in self.index]
        if not bitmaps:
            return BitMap()
        return BitMap.intersection(*bitmaps)

    def save(self, path):
        env = lmdb.open(path, map_size=2**40)
        with env.begin(write=True) as txn:
            for token, bitmap in self.index.items():
                txn.put(token.encode(), bitmap.serialize())
        env.close()

    @classmethod
    def load(cls, path):
        idx = cls()
        env = lmdb.open(path, readonly=True)
        with env.begin() as txn:
            cursor = txn.cursor()
            for key, value in cursor:
                idx.index[key.decode()] = BitMap.deserialize(value)
        env.close()
        return idx

    def __ior__(self, other):
        for token, bitmap in other.index.items():
            if token in self.index:
                self.index[token] |= bitmap
            else:
                self.index[token] = bitmap.copy()
        return self

    def __len__(self):
        return len(self.index)
    
    def __repr__(self):
        tokens = sorted(self.index.keys())
        preview = ", ".join(tokens[:5])
        if len(tokens) > 5:
            preview += ", ..."
        return f"BitmapIndex(tokens={len(tokens)}, positions={max(max(b) for b in self.index.values()) + 1 if self.index else 0}, keys=[{preview}])"
    
    def __contains__(self, token):
        return token in self.index

    def __getitem__(self, token):
        return self.index[token]
    
    def __iter__(self):
        return iter(self.index)

    def __bool__(self):
        return bool(self.index)