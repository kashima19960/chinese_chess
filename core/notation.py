"""Chinese notation generator for chess moves.

This module provides the NotationGenerator class which converts chess moves
to traditional Chinese notation format (e.g., "炮二平五").

Typical usage example:
    generator = NotationGenerator(board)
    notation = generator.generate_notation((0, 1), (0, 4))
"""

from typing import Tuple

from core.board import Board
from core.constants import (
    BLACK,
    BLACK_COL_TO_CHINESE,
    BOARD_ROWS,
    PIECE_CHINESE_NAMES,
    RED,
    RED_COL_TO_CHINESE,
    get_piece_color,
)


class NotationGenerator:
    """Chinese chess notation generator.

    Generates traditional Chinese notation for chess moves following
    the standard format: piece name + column + action + target.

    Attributes:
        board: The Board instance to generate notation for.
    """

    def __init__(self, board: Board) -> None:
        """Initialize the notation generator.

        Args:
            board: The Board instance to use.
        """
        self.board = board

    def generate_notation(
        self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> str:
        """Generate Chinese notation for a move.

        Args:
            from_pos: Starting position (row, col).
            to_pos: Target position (row, col).

        Returns:
            Chinese notation string, e.g., "炮二平五".
        """
        r1, c1 = from_pos
        r2, c2 = to_pos

        piece = self.board.get_piece(r1, c1)
        if not piece:
            return ""

        color = get_piece_color(piece)
        piece_name = PIECE_CHINESE_NAMES.get(piece, "")

        # Get column mapping based on color
        col_map = RED_COL_TO_CHINESE if color == RED else BLACK_COL_TO_CHINESE

        # Calculate move direction and distance
        dr = r2 - r1
        dc = c2 - c1

        # Check if position prefix is needed (multiple same pieces in column)
        prefix = self._get_position_prefix(r1, c1, piece, color)

        # Build starting notation
        if prefix:
            start_notation = prefix + piece_name
        else:
            start_notation = piece_name + col_map[c1]

        # Determine move direction and target
        if dc == 0:
            # Vertical movement
            if dr > 0:
                direction = "进"
                distance = abs(dr)
            else:
                direction = "退"
                distance = abs(dr)

            # Advisors and bishops use target column notation
            if piece.upper() in ['A', 'B']:
                target = col_map[c2]
            else:
                target = self._number_to_chinese(distance, color)
        else:
            # Horizontal movement
            direction = "平"
            target = col_map[c2]

        return start_notation + direction + target

    def _get_position_prefix(
        self, row: int, col: int, piece: str, color: int
    ) -> str:
        """Get position prefix for disambiguating identical pieces.

        Args:
            row: Piece row position.
            col: Piece column position.
            piece: The piece character.
            color: Piece color (RED or BLACK).

        Returns:
            Position prefix string ("前"/"后"/"中" etc.) or empty string.
        """
        # Find same pieces in the column
        same_pieces = []
        for r in range(BOARD_ROWS):
            p = self.board.get_piece(r, col)
            if p == piece:
                same_pieces.append(r)

        if len(same_pieces) <= 1:
            return ""

        # Sort from player's perspective
        same_pieces.sort(reverse=(color == RED))

        # Find current piece position
        idx = same_pieces.index(row)

        if len(same_pieces) == 2:
            return "前" if idx == 0 else "后"
        elif len(same_pieces) == 3:
            return ["前", "中", "后"][idx]
        elif len(same_pieces) == 4:
            return ["前", "二", "三", "四"][idx]
        else:
            return ["前", "二", "三", "四", "五"][idx] if idx < 5 else "后"

    def _number_to_chinese(self, num: int, color: int) -> str:
        """Convert a number to Chinese notation.

        Args:
            num: The number to convert.
            color: RED uses Chinese numerals, BLACK uses Arabic numerals.

        Returns:
            Chinese numeral string or Arabic numeral string.
        """
        if color == RED:
            chinese_nums = {
                1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
                6: "六", 7: "七", 8: "八", 9: "九", 10: "十"
            }
            return chinese_nums.get(num, str(num))
        else:
            return str(num)
