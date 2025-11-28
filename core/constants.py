"""
Constants and configuration for Chinese Chess.
"""

from typing import Final

# ===========================
# 阵营定义 (Camp Definition)
# ===========================
RED: Final[int] = 1      # 红方(先手/玩家)
BLACK: Final[int] = -1   # 黑方(后手/电脑)

# ===========================
# 棋子编码 (Piece Encoding)
# ===========================
# 红方棋子
RED_ROOK: Final[str] = 'R'      # 车
RED_KNIGHT: Final[str] = 'N'    # 马
RED_BISHOP: Final[str] = 'B'    # 相
RED_ADVISOR: Final[str] = 'A'   # 仕
RED_KING: Final[str] = 'K'      # 帅
RED_CANNON: Final[str] = 'C'    # 炮
RED_PAWN: Final[str] = 'P'      # 兵

# 黑方棋子
BLACK_ROOK: Final[str] = 'r'    # 车
BLACK_KNIGHT: Final[str] = 'n'  # 马
BLACK_BISHOP: Final[str] = 'b'  # 象
BLACK_ADVISOR: Final[str] = 'a' # 士
BLACK_KING: Final[str] = 'k'    # 将
BLACK_CANNON: Final[str] = 'c'  # 炮
BLACK_PAWN: Final[str] = 'p'    # 卒

# 所有棋子集合
RED_PIECES: Final[set[str]] = {'R', 'N', 'B', 'A', 'K', 'C', 'P'}
BLACK_PIECES: Final[set[str]] = {'r', 'n', 'b', 'a', 'k', 'c', 'p'}
ALL_PIECES: Final[set[str]] = RED_PIECES | BLACK_PIECES

# ===========================
# 棋子分值 (Piece Values)
# ===========================
PIECE_VALUES: Final[dict[str, int]] = {
    'R': 900, 'r': 900,   # 车
    'N': 400, 'n': 400,   # 马
    'B': 200, 'b': 200,   # 相/象
    'A': 200, 'a': 200,   # 仕/士
    'K': 10000, 'k': 10000,  # 帅/将
    'C': 450, 'c': 450,   # 炮
    'P': 100, 'p': 100,   # 兵/卒(基础值,过河加倍)
}

# ===========================
# 棋盘尺寸 (Board Dimensions)
# ===========================
BOARD_ROWS: Final[int] = 10
BOARD_COLS: Final[int] = 9

# ===========================
# 九宫定义 (Palace Boundaries)
# ===========================
RED_PALACE_ROWS: Final[tuple[int, int]] = (0, 2)    # 红方九宫: row 0-2
RED_PALACE_COLS: Final[tuple[int, int]] = (3, 5)    # 红方九宫: col 3-5
BLACK_PALACE_ROWS: Final[tuple[int, int]] = (7, 9)  # 黑方九宫: row 7-9
BLACK_PALACE_COLS: Final[tuple[int, int]] = (3, 5)  # 黑方九宫: col 3-5

# ===========================
# 河界定义 (River Boundary)
# ===========================
RIVER_ROW: Final[int] = 4  # row <= 4 为红方，row >= 5 为黑方

# ===========================
# 初始FEN (Initial FEN String)
# ===========================
INITIAL_FEN: Final[str] = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w"

# ===========================
# 中文列号映射 (Chinese Column Notation)
# ===========================
# 红方视角: 从右向左数 (1-9)
RED_COL_TO_CHINESE: Final[dict[int, str]] = {
    0: '九', 1: '八', 2: '七', 3: '六', 4: '五',
    5: '四', 6: '三', 7: '二', 8: '一'
}

# 黑方视角: 从右向左数 (1-9)
BLACK_COL_TO_CHINESE: Final[dict[int, str]] = {
    0: '1', 1: '2', 2: '3', 3: '4', 4: '5',
    5: '6', 6: '7', 7: '8', 8: '9'
}

# ===========================
# 中文棋子名称 (Chinese Piece Names)
# ===========================
PIECE_CHINESE_NAMES: Final[dict[str, str]] = {
    'R': '车', 'r': '车',
    'N': '马', 'n': '马',
    'B': '相', 'b': '象',
    'A': '仕', 'a': '士',
    'K': '帅', 'k': '将',
    'C': '炮', 'c': '炮',
    'P': '兵', 'p': '卒',
}

# ===========================
# 辅助函数 (Helper Functions)
# ===========================
def get_piece_color(piece: str) -> int:
    """获取棋子颜色"""
    if piece in RED_PIECES:
        return RED
    elif piece in BLACK_PIECES:
        return BLACK
    return 0

def is_in_palace(row: int, col: int, color: int) -> bool:
    """判断位置是否在指定颜色的九宫内"""
    if color == RED:
        return (RED_PALACE_ROWS[0] <= row <= RED_PALACE_ROWS[1] and
                RED_PALACE_COLS[0] <= col <= RED_PALACE_COLS[1])
    else:
        return (BLACK_PALACE_ROWS[0] <= row <= BLACK_PALACE_ROWS[1] and
                BLACK_PALACE_COLS[0] <= col <= BLACK_PALACE_COLS[1])

def is_in_bounds(row: int, col: int) -> bool:
    """判断坐标是否在棋盘内"""
    return 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS

def can_cross_river(piece: str, row: int) -> bool:
    """判断象/相是否能过河"""
    color = get_piece_color(piece)
    if piece.upper() == 'B':  # 象/相
        if color == RED:
            return row <= RIVER_ROW
        else:
            return row >= RIVER_ROW + 1
    return True
