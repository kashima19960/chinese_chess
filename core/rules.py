"""Rule engine for move validation and game state checking.

This module provides the RuleEngine class which handles all chess rule
validation including move legality, check detection, and game end conditions.

Typical usage example:
    engine = RuleEngine(board)
    moves = engine.get_legal_moves(0, 0)
    is_check = engine.is_in_check(RED)
"""

from typing import List, Optional, Tuple

from core.board import Board
from core.constants import (
    BLACK,
    RED,
    RIVER_ROW,
    can_cross_river,
    get_piece_color,
    is_in_bounds,
    is_in_palace,
)


class RuleEngine:
    """Chinese Chess rule validation engine.

    Handles all rule checking including:
    - Legal move generation for each piece type
    - Check and checkmate detection
    - Stalemate detection
    - Flying general rule validation

    Attributes:
        board: The Board instance to validate moves on.
    """

    def __init__(self, board: Board) -> None:
        """Initialize the rule engine.

        Args:
            board: The Board instance to use for validation.
        """
        self.board = board

    def get_legal_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get all legal moves for a piece at the given position.

        Args:
            row: Board row of the piece.
            col: Board column of the piece.

        Returns:
            List of legal destination positions (row, col).
        """
        piece = self.board.get_piece(row, col)
        if not piece:
            return []

        # Get pseudo-legal moves (ignoring check)
        moves = self._get_pseudo_legal_moves(row, col, piece)

        # Filter moves that would leave the king in check
        legal_moves = []
        for to_pos in moves:
            if self._is_legal_move((row, col), to_pos):
                legal_moves.append(to_pos)

        return legal_moves

    def _get_pseudo_legal_moves(
        self, row: int, col: int, piece: str
    ) -> List[Tuple[int, int]]:
        """Get pseudo-legal moves (not checking for check).

        Args:
            row: Board row of the piece.
            col: Board column of the piece.
            piece: The piece character.

        Returns:
            List of possible destination positions.
        """
        piece_type = piece.upper()
        color = get_piece_color(piece)

        move_handlers = {
            'R': self._get_rook_moves,
            'N': self._get_knight_moves,
            'B': self._get_bishop_moves,
            'A': self._get_advisor_moves,
            'K': self._get_king_moves,
            'C': self._get_cannon_moves,
            'P': self._get_pawn_moves,
        }

        handler = move_handlers.get(piece_type)
        if handler:
            return handler(row, col, color)
        return []

    def _get_rook_moves(
        self, row: int, col: int, color: int
    ) -> List[Tuple[int, int]]:
        """Get rook (车) moves: straight lines in all four directions.

        Args:
            row: Board row of the piece.
            col: Board column of the piece.
            color: Piece color (RED or BLACK).

        Returns:
            List of possible destination positions.
        """
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while is_in_bounds(r, c):
                target = self.board.get_piece(r, c)
                if target is None:
                    moves.append((r, c))
                elif get_piece_color(target) != color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc

        return moves

    def _get_knight_moves(
        self, row: int, col: int, color: int
    ) -> List[Tuple[int, int]]:
        """Get knight (马) moves: L-shape with blocking check.

        The knight moves in an L-shape but can be blocked by pieces
        adjacent to its starting position.

        Args:
            row: Board row of the piece.
            col: Board column of the piece.
            color: Piece color (RED or BLACK).

        Returns:
            List of possible destination positions.
        """
        moves = []

        # (delta_row, delta_col, blocking_position)
        knight_moves = [
            (2, 1, (1, 0)),
            (2, -1, (1, 0)),
            (-2, 1, (-1, 0)),
            (-2, -1, (-1, 0)),
            (1, 2, (0, 1)),
            (-1, 2, (0, 1)),
            (1, -2, (0, -1)),
            (-1, -2, (0, -1)),
        ]

        for dr, dc, (block_dr, block_dc) in knight_moves:
            r2, c2 = row + dr, col + dc
            block_r, block_c = row + block_dr, col + block_dc

            if not is_in_bounds(r2, c2):
                continue

            # Check for blocking piece (蹩马腿)
            if self.board.get_piece(block_r, block_c) is not None:
                continue

            target = self.board.get_piece(r2, c2)
            if target is None or get_piece_color(target) != color:
                moves.append((r2, c2))

        return moves

    def _get_bishop_moves(
        self, row: int, col: int, color: int
    ) -> List[Tuple[int, int]]:
        """Get bishop (相/象) moves: diagonal with blocking, no river crossing.

        The bishop moves diagonally two points but can be blocked
        and cannot cross the river.

        Args:
            row: Board row of the piece.
            col: Board column of the piece.
            color: Piece color (RED or BLACK).

        Returns:
            List of possible destination positions.
        """
        moves = []

        # (delta_row, delta_col, blocking_position)
        bishop_moves = [
            (2, 2, (1, 1)),
            (2, -2, (1, -1)),
            (-2, 2, (-1, 1)),
            (-2, -2, (-1, -1)),
        ]

        for dr, dc, (block_dr, block_dc) in bishop_moves:
            r2, c2 = row + dr, col + dc
            block_r, block_c = row + block_dr, col + block_dc

            if not is_in_bounds(r2, c2):
                continue

            # Check river crossing
            piece = 'B' if color == RED else 'b'
            if not can_cross_river(piece, r2):
                continue

            # Check blocking piece (塞象眼)
            if self.board.get_piece(block_r, block_c) is not None:
                continue

            target = self.board.get_piece(r2, c2)
            if target is None or get_piece_color(target) != color:
                moves.append((r2, c2))

        return moves

    def _get_advisor_moves(
        self, row: int, col: int, color: int
    ) -> List[Tuple[int, int]]:
        """Get advisor (仕/士) moves: diagonal within palace.

        Args:
            row: Board row of the piece.
            col: Board column of the piece.
            color: Piece color (RED or BLACK).

        Returns:
            List of possible destination positions.
        """
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dr, dc in directions:
            r2, c2 = row + dr, col + dc

            if not is_in_palace(r2, c2, color):
                continue

            target = self.board.get_piece(r2, c2)
            if target is None or get_piece_color(target) != color:
                moves.append((r2, c2))

        return moves

    def _get_king_moves(
        self, row: int, col: int, color: int
    ) -> List[Tuple[int, int]]:
        """Get king (帅/将) moves: orthogonal within palace.

        Args:
            row: Board row of the piece.
            col: Board column of the piece.
            color: Piece color (RED or BLACK).

        Returns:
            List of possible destination positions.
        """
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dr, dc in directions:
            r2, c2 = row + dr, col + dc

            if not is_in_palace(r2, c2, color):
                continue

            target = self.board.get_piece(r2, c2)
            if target is None or get_piece_color(target) != color:
                moves.append((r2, c2))

        return moves

    def _get_cannon_moves(
        self, row: int, col: int, color: int
    ) -> List[Tuple[int, int]]:
        """Get cannon (炮) moves: straight lines, jump to capture.

        The cannon moves like a rook but must jump exactly one piece
        to capture.

        Args:
            row: Board row of the piece.
            col: Board column of the piece.
            color: Piece color (RED or BLACK).

        Returns:
            List of possible destination positions.
        """
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dr, dc in directions:
            jumped = False
            r, c = row + dr, col + dc

            while is_in_bounds(r, c):
                target = self.board.get_piece(r, c)

                if target is None:
                    if not jumped:
                        moves.append((r, c))
                else:
                    if not jumped:
                        jumped = True
                    else:
                        if get_piece_color(target) != color:
                            moves.append((r, c))
                        break

                r += dr
                c += dc

        return moves

    def _get_pawn_moves(
        self, row: int, col: int, color: int
    ) -> List[Tuple[int, int]]:
        """Get pawn (兵/卒) moves: forward, sideways after crossing river.

        Args:
            row: Board row of the piece.
            col: Board column of the piece.
            color: Piece color (RED or BLACK).

        Returns:
            List of possible destination positions.
        """
        moves = []

        if color == RED:
            crossed = row > RIVER_ROW
            forward = 1
        else:
            crossed = row < RIVER_ROW + 1
            forward = -1

        # Forward move
        r2, c2 = row + forward, col
        if is_in_bounds(r2, c2):
            target = self.board.get_piece(r2, c2)
            if target is None or get_piece_color(target) != color:
                moves.append((r2, c2))

        # Sideways moves after crossing river
        if crossed:
            for dc in [-1, 1]:
                r2, c2 = row, col + dc
                if is_in_bounds(r2, c2):
                    target = self.board.get_piece(r2, c2)
                    if target is None or get_piece_color(target) != color:
                        moves.append((r2, c2))

        return moves

    def _is_legal_move(
        self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> bool:
        """Check if a move is legal (considering check and flying general).

        Args:
            from_pos: Starting position (row, col).
            to_pos: Target position (row, col).

        Returns:
            True if the move is legal, False otherwise.
        """
        # Create temporary board to test the move
        temp_board = self.board.copy()
        r1, c1 = from_pos
        r2, c2 = to_pos

        piece = temp_board.get_piece(r1, c1)
        if not piece:
            return False

        color = get_piece_color(piece)

        # Execute the move
        temp_board.set_piece(r2, c2, piece)
        temp_board.set_piece(r1, c1, None)

        # Create temporary rule engine
        temp_engine = RuleEngine(temp_board)

        # Check if move leaves own king in check
        if temp_engine.is_in_check(color):
            return False

        # Check for flying general
        if temp_engine._is_flying_general():
            return False

        return True

    def is_in_check(self, color: int) -> bool:
        """Check if the specified color's king is in check.

        Args:
            color: RED or BLACK.

        Returns:
            True if in check, False otherwise.
        """
        # Find the king
        king_pos = self.board.find_king(color)
        if not king_pos:
            return False

        # Check if any enemy piece can attack the king
        enemy_color = -color
        enemy_pieces = self.board.get_all_pieces(enemy_color)

        for r, c, piece in enemy_pieces:
            pseudo_moves = self._get_pseudo_legal_moves(r, c, piece)
            if king_pos in pseudo_moves:
                return True

        return False

    def _is_flying_general(self) -> bool:
        """Check for flying general (kings facing each other).

        The flying general rule states that the two kings cannot
        face each other on the same column with no pieces between.

        Returns:
            True if flying general condition exists, False otherwise.
        """
        red_king_pos = self.board.find_king(RED)
        black_king_pos = self.board.find_king(BLACK)

        if not red_king_pos or not black_king_pos:
            return False

        r1, c1 = red_king_pos
        r2, c2 = black_king_pos

        # Must be on the same column
        if c1 != c2:
            return False

        # Check if there are pieces between the kings
        min_row = min(r1, r2)
        max_row = max(r1, r2)

        for row in range(min_row + 1, max_row):
            if self.board.get_piece(row, c1) is not None:
                return False

        return True

    def is_checkmate(self, color: int) -> bool:
        """Check if the specified color is checkmated.

        Args:
            color: RED or BLACK.

        Returns:
            True if checkmated, False otherwise.
        """
        # Must be in check first
        if not self.is_in_check(color):
            return False

        # Check if there are any legal moves
        pieces = self.board.get_all_pieces(color)
        for r, c, piece in pieces:
            legal_moves = self.get_legal_moves(r, c)
            if legal_moves:
                return False

        return True

    def is_stalemate(self, color: int) -> bool:
        """Check if the specified color is stalemated.

        Stalemate occurs when a player has no legal moves but is not in check.

        Args:
            color: RED or BLACK.

        Returns:
            True if stalemated, False otherwise.
        """
        # Cannot be in check
        if self.is_in_check(color):
            return False

        # Check if there are any legal moves
        pieces = self.board.get_all_pieces(color)
        for r, c, piece in pieces:
            legal_moves = self.get_legal_moves(r, c)
            if legal_moves:
                return False

        return True

    def get_game_result(self) -> Optional[int]:
        """Get the game result.

        Returns:
            RED: Red wins.
            BLACK: Black wins.
            None: Game is not over.
        """
        current_color = self.board.current_player

        # Check if current player is checkmated
        if self.is_checkmate(current_color):
            return -current_color

        # Check if current player is stalemated
        if self.is_stalemate(current_color):
            return -current_color

        return None
