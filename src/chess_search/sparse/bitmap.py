import json
from pyroaring import BitMap
from chess_search.utils import position_to_tokens
import lmdb


class BitmapIndex:
    def __init__(self):
        self.index = {}
        self._next_id = 0
        self._metadata = []

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
        env = lmdb.open(path, map_size=2**40, max_dbs=2)
        bitmap_db = env.open_db(b"bitmaps")
        meta_db = env.open_db(b"metadata")
        with env.begin(write=True) as txn:
            for token, bitmap in self.index.items():
                txn.put(token.encode(), bitmap.serialize(), db=bitmap_db)
            txn.put(b"next_id", str(self._next_id).encode(), db=meta_db)
            txn.put(b"metadata", json.dumps(self._metadata).encode(), db=meta_db)
        env.close()

    @classmethod
    def load(cls, path):
        idx = cls()
        env = lmdb.open(path, readonly=True, max_dbs=2)
        bitmap_db = env.open_db(b"bitmaps")
        meta_db = env.open_db(b"metadata")
        with env.begin(buffers=False) as txn:
            cursor = txn.cursor(db=bitmap_db)
            for key, value in cursor:
                idx.index[key.decode()] = BitMap.deserialize(value)
            meta_raw = txn.get(b"metadata", db=meta_db)
            if meta_raw:
                idx._metadata = [tuple(x) for x in json.loads(meta_raw)]
                idx._next_id = int(txn.get(b"next_id", db=meta_db))
        env.close()
        return idx

    def add_source(self, source_id, boards):
        for move_idx, board in enumerate(boards):
            self.add(self._next_id, board)
            self._metadata.append((source_id, move_idx))
            self._next_id += 1

    def resolve(self, bitmap):
        return [self._metadata[pos_id] for pos_id in bitmap]

    @classmethod
    def build_index(cls, sources, total=None):
        from tqdm import tqdm
        idx = cls()
        for source_id, boards in tqdm(sources, total=total):
            idx.add_source(source_id, boards)
        return idx

    def __ior__(self, other):
        offset = self._next_id
        for token, bitmap in other.index.items():
            shifted = BitMap(pos_id + offset for pos_id in bitmap)
            if token in self.index:
                self.index[token] |= shifted
            else:
                self.index[token] = shifted
        self._metadata.extend(other._metadata)
        self._next_id += other._next_id
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
