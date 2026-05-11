def on_file(idx, piece, file):
    return idx.union([f"{piece}_{file}{r}" for r in range(1, 9)])


def on_rank(idx, piece, rank):
    return idx.union([f"{piece}_{f}{rank}" for f in "abcdefgh"])


def in_center(idx, piece):
    return idx.union([f"{piece}_{sq}" for sq in ["d4", "d5", "e4", "e5"]])


def on_kingside(idx, piece):
    return idx.union([f"{piece}_{f}{r}" for f in "efgh" for r in range(1, 9)])


def on_queenside(idx, piece):
    return idx.union([f"{piece}_{f}{r}" for f in "abcd" for r in range(1, 9)])


def anywhere(idx, piece):
    return idx.union([f"{piece}_{f}{r}" for f in "abcdefgh" for r in range(1, 9)])


def on_color(idx, piece, color):
    squares = [
        f"{f}{r}"
        for f in "abcdefgh"
        for r in range(1, 9)
        if (ord(f) - ord("a") + r - 1) % 2 == (0 if color == "dark" else 1)
    ]
    return idx.union([f"{piece}_{sq}" for sq in squares])
