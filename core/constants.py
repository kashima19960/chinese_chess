"""Constants and configuration for Chinese Chess.

This module defines all game constants including piece encodings, board
dimensions, position boundaries, and Chinese notation mappings.

Typical usage example:
    from core.constants import RED, BLACK, INITIAL_FEN, get_piece_color
    
    color = get_piece_color('R')  # Returns RED
"""

from typing import Final


# =============================================================================
# Player/Camp Constants
# =============================================================================
RED: Final[int] = 1       # Red player (first move)
BLACK: Final[int] = -1    # Black player (second move)


# =============================================================================
# Piece Encoding (FEN Standard)
# =============================================================================
# Red pieces (uppercase)
RED_ROOK: Final[str] = 'R'      # Chariot (车)
RED_KNIGHT: Final[str] = 'N'    # Horse (马)
RED_BISHOP: Final[str] = 'B'    # Elephant (相)
RED_ADVISOR: Final[str] = 'A'   # Advisor (仕)
RED_KING: Final[str] = 'K'      # General (帅)
RED_CANNON: Final[str] = 'C'    # Cannon (炮)
RED_PAWN: Final[str] = 'P'      # Soldier (兵)

# Black pieces (lowercase)
BLACK_ROOK: Final[str] = 'r'    # Chariot (车)
BLACK_KNIGHT: Final[str] = 'n'  # Horse (马)
BLACK_BISHOP: Final[str] = 'b'  # Elephant (象)
BLACK_ADVISOR: Final[str] = 'a' # Advisor (士)
BLACK_KING: Final[str] = 'k'    # General (将)
BLACK_CANNON: Final[str] = 'c'  # Cannon (炮)
BLACK_PAWN: Final[str] = 'p'    # Soldier (卒)

# Piece sets for validation
RED_PIECES: Final[frozenset] = frozenset({'R', 'N', 'B', 'A', 'K', 'C', 'P'})
BLACK_PIECES: Final[frozenset] = frozenset({'r', 'n', 'b', 'a', 'k', 'c', 'p'})
ALL_PIECES: Final[frozenset] = RED_PIECES | BLACK_PIECES


# =============================================================================
# Piece Values (for AI evaluation)
# =============================================================================
PIECE_VALUES: Final[dict] = {
    'R': 900, 'r': 900,      # Chariot - most valuable
    'N': 400, 'n': 400,      # Horse
    'B': 200, 'b': 200,      # Elephant
    'A': 200, 'a': 200,      # Advisor
    'K': 10000, 'k': 10000,  # King - game-ending value
    'C': 450, 'c': 450,      # Cannon
    'P': 100, 'p': 100,      # Pawn (base value, doubles after crossing river)
}


# =============================================================================
# Board Dimensions
# =============================================================================
BOARD_ROWS: Final[int] = 10  # 10 rows (0-9)
BOARD_COLS: Final[int] = 9   # 9 columns (0-8)


# =============================================================================
# Palace Boundaries (9-point grid for King/Advisor)
# =============================================================================
RED_PALACE_ROWS: Final[tuple] = (0, 2)    # Red palace: rows 0-2
RED_PALACE_COLS: Final[tuple] = (3, 5)    # Red palace: cols 3-5
BLACK_PALACE_ROWS: Final[tuple] = (7, 9)  # Black palace: rows 7-9
BLACK_PALACE_COLS: Final[tuple] = (3, 5)  # Black palace: cols 3-5


# =============================================================================
# River Boundary
# =============================================================================
RIVER_ROW: Final[int] = 4  # row <= 4 is Red's side, row >= 5 is Black's side


# =============================================================================
# Initial Position (FEN Format)
# =============================================================================
INITIAL_FEN: Final[str] = (
    "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w"
)


# =============================================================================
# Chinese Notation Mappings
# =============================================================================
# Column numbers from Red's perspective (right to left: 1-9)
RED_COL_TO_CHINESE: Final[dict] = {
    0: '九', 1: '八', 2: '七', 3: '六', 4: '五',
    5: '四', 6: '三', 7: '二', 8: '一'
}

# Column numbers from Black's perspective (using Arabic numerals)
BLACK_COL_TO_CHINESE: Final[dict] = {
    0: '1', 1: '2', 2: '3', 3: '4', 4: '5',
    5: '6', 6: '7', 7: '8', 8: '9'
}

# Chinese piece names for display
PIECE_CHINESE_NAMES: Final[dict] = {
    'R': '车', 'r': '车',
    'N': '马', 'n': '马',
    'B': '相', 'b': '象',
    'A': '仕', 'a': '士',
    'K': '帅', 'k': '将',
    'C': '炮', 'c': '炮',
    'P': '兵', 'p': '卒',
}


# =============================================================================
# Helper Functions
# =============================================================================
def get_piece_color(piece: str) -> int:
    """Get the color (player) of a piece.
    
    Args:
        piece: Single character piece code (e.g., 'R', 'n').
    
    Returns:
        RED (1) for red pieces, BLACK (-1) for black pieces, 0 for invalid.
    """
    if piece in RED_PIECES:
        return RED
    if piece in BLACK_PIECES:
        return BLACK
    return 0


def is_in_palace(row: int, col: int, color: int) -> bool:
    """Check if a position is within a player's palace.
    
    Args:
        row: Board row (0-9).
        col: Board column (0-8).
        color: Player color (RED or BLACK).
    
    Returns:
        True if the position is within the palace, False otherwise.
    """
    if color == RED:
        return (RED_PALACE_ROWS[0] <= row <= RED_PALACE_ROWS[1] and
                RED_PALACE_COLS[0] <= col <= RED_PALACE_COLS[1])
    return (BLACK_PALACE_ROWS[0] <= row <= BLACK_PALACE_ROWS[1] and
            BLACK_PALACE_COLS[0] <= col <= BLACK_PALACE_COLS[1])


def is_in_bounds(row: int, col: int) -> bool:
    """Check if coordinates are within the board boundaries.
    
    Args:
        row: Board row.
        col: Board column.
    
    Returns:
        True if within bounds, False otherwise.
    """
    return 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS


def can_cross_river(piece: str, row: int) -> bool:
    """Check if an Elephant piece can be at the given row.
    
    Elephants (相/象) cannot cross the river. This function validates
    that an elephant is on its own side of the board.
    
    Args:
        piece: The piece character.
        row: Target row position.
    
    Returns:
        True if the piece can be at the row, False if restricted.
    """
    color = get_piece_color(piece)
    if piece.upper() == 'B':  # Elephant
        if color == RED:
            return row <= RIVER_ROW
        return row >= RIVER_ROW + 1
    return True
