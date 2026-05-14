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

def empty_square(idx, square):
    all_pieces = [f"{p}_{square}" for p in "PNBRQKpnbrqk"]
    occupied = idx.union(all_pieces)
    return idx._all_positions - occupied

def on_square(idx, square):
    """Any piece at all on this square."""
    return idx.union([f"{p}_{square}" for p in "PNBRQKpnbrqk"])

def any_white_on(idx, square):
    return idx.union([f"{p}_{square}" for p in "PNBRQK"])

def any_black_on(idx, square):
    return idx.union([f"{p}_{square}" for p in "pnbrqk"])

def piece_on(idx, piece_type, square):
    return idx.union([f"{piece_type.upper()}_{square}", f"{piece_type.lower()}_{square}"])

def open_file(idx, file):
    white_pawns = on_file(idx, "P", file)
    black_pawns = on_file(idx, "p", file)
    return idx._all_positions - white_pawns - black_pawns

def semi_open_file(idx, file, color):
    if color == "white":
        return (idx._all_positions - on_file(idx, "P", file)) & on_file(idx, "p", file)
    else:
        return (idx._all_positions - on_file(idx, "p", file)) & on_file(idx, "P", file)
    
def flipcolor(tokens):
    return [f"{t[0].swapcase()}{t[1:]}" for t in tokens]

def mirror_vertical(tokens):
    flip = str.maketrans("abcdefgh", "hgfedcba")
    return [t[0] + "_" + t[2].translate(flip) + t[3:] for t in tokens]

def mirror_horizontal(tokens):
    flip = str.maketrans("12345678", "87654321")
    return [t[0] + "_" + t[2] + t[3].translate(flip) for t in tokens]

def rotate_180(tokens):
    return mirror_horizontal(mirror_vertical(tokens))
