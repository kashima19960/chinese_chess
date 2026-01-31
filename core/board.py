"""Board state management with FEN parsing.

This module provides the Board class which manages the chess board state,
including piece positions, move history, and FEN string conversion.

Typical usage example:
    board = Board(INITIAL_FEN)
    board.move_piece((0, 0), (0, 1))
    fen = board.to_fen()
"""

from typing import List, Optional, Tuple

from core.constants import (
    ALL_PIECES,
    BLACK,
    BLACK_PIECES,
    BOARD_COLS,
    BOARD_ROWS,
    INITIAL_FEN,
    RED,
    RED_PIECES,
    is_in_bounds,
)


class Board:
    """Manages the Chinese Chess board state.
    
    This class handles all board operations including piece placement,
    movement, FEN string parsing, and game history management.
    
    Attributes:
        board: 2D list representing the 10x9 board grid.
        current_player: The player to move (RED or BLACK).
        history: List of previous FEN states for undo support.
        move_history: List of moves made (from_pos, to_pos tuples).
    """
    
    def __init__(self, fen: str = INITIAL_FEN) -> None:
        """Initialize the board from a FEN string.
        
        Args:
            fen: FEN string representing the board state.
                 Defaults to the standard starting position.
        """
        self.board: List[List[Optional[str]]] = [
            [None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)
        ]
        self.current_player: int = RED
        self.history: List[str] = []
        self.move_history: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []
        
        self.load_fen(fen)
    
    def load_fen(self, fen: str) -> None:
        """Load board state from a FEN string.
        
        FEN format: "board_layout current_player"
        Example: "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w"
        
        Args:
            fen: FEN string to parse.
        
        Raises:
            ValueError: If the FEN string is invalid.
        """
        parts = fen.split()
        if not parts:
            raise ValueError("Invalid FEN string: empty")
        
        board_str = parts[0]
        rows = board_str.split('/')
        
        if len(rows) != BOARD_ROWS:
            raise ValueError(f"FEN must have {BOARD_ROWS} rows, got {len(rows)}")
        
        # Clear the board
        self.board = [
            [None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)
        ]
        
        # Parse each row (FEN starts from Black's side: row 9 -> 0)
        for i, row_str in enumerate(rows):
            row_idx = BOARD_ROWS - 1 - i
            col_idx = 0
            
            for char in row_str:
                if char.isdigit():
                    col_idx += int(char)
                elif char in ALL_PIECES:
                    if col_idx >= BOARD_COLS:
                        raise ValueError(f"Too many pieces in row {row_idx}")
                    self.board[row_idx][col_idx] = char
                    col_idx += 1
        
        # Parse current player
        if len(parts) > 1:
            self.current_player = RED if parts[1] == 'w' else BLACK
        else:
            self.current_player = RED
    
    def to_fen(self) -> str:
        """Convert current board state to FEN string.
        
        Returns:
            FEN string representation of the board.
        """
        rows = []
        for row_idx in range(BOARD_ROWS - 1, -1, -1):
            row_str = ""
            empty_count = 0
            
            for col_idx in range(BOARD_COLS):
                piece = self.board[row_idx][col_idx]
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += piece
            
            if empty_count > 0:
                row_str += str(empty_count)
            
            rows.append(row_str)
        
        board_str = '/'.join(rows)
        player_str = 'w' if self.current_player == RED else 'b'
        
        return f"{board_str} {player_str}"
    
    def get_piece(self, row: int, col: int) -> Optional[str]:
        """Get the piece at a specific position.
        
        Args:
            row: Board row (0-9).
            col: Board column (0-8).
        
        Returns:
            Piece character or None if empty/out of bounds.
        """
        if not is_in_bounds(row, col):
            return None
        return self.board[row][col]
    
    def set_piece(self, row: int, col: int, piece: Optional[str]) -> None:
        """Set a piece at a specific position.
        
        Args:
            row: Board row (0-9).
            col: Board column (0-8).
            piece: Piece character or None to clear.
        """
        if is_in_bounds(row, col):
            self.board[row][col] = piece
    
    def move_piece(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int]
    ) -> Optional[str]:
        """Move a piece from one position to another.
        
        Args:
            from_pos: Starting position (row, col).
            to_pos: Destination position (row, col).
        
        Returns:
            The captured piece if any, None otherwise.
        """
        r1, c1 = from_pos
        r2, c2 = to_pos
        
        piece = self.get_piece(r1, c1)
        captured = self.get_piece(r2, c2)
        
        # Save current state for undo
        self.history.append(self.to_fen())
        self.move_history.append((from_pos, to_pos))
        
        # Execute the move
        self.set_piece(r2, c2, piece)
        self.set_piece(r1, c1, None)
        
        # Switch player
        self.current_player = -self.current_player
        
        return captured
    
    def undo_move(self) -> bool:
        """Undo the last move.
        
        Returns:
            True if undo was successful, False if no history.
        """
        if not self.history:
            return False
        
        last_fen = self.history.pop()
        self.move_history.pop()
        self.load_fen(last_fen)
        
        return True
    
    def copy(self) -> 'Board':
        """Create a deep copy of the board.
        
        Returns:
            A new Board instance with the same state.
        """
        new_board = Board()
        new_board.load_fen(self.to_fen())
        new_board.history = self.history.copy()
        new_board.move_history = self.move_history.copy()
        return new_board
    
    def find_king(self, color: int) -> Optional[Tuple[int, int]]:
        """Find the position of a player's King.
        
        Args:
            color: Player color (RED or BLACK).
        
        Returns:
            (row, col) tuple or None if not found.
        """
        king = 'K' if color == RED else 'k'
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.board[row][col] == king:
                    return (row, col)
        return None
    
    def get_all_pieces(
        self, color: int
    ) -> List[Tuple[int, int, str]]:
        """Get all pieces belonging to a player.
        
        Args:
            color: Player color (RED or BLACK).
        
        Returns:
            List of (row, col, piece) tuples.
        """
        pieces = []
        target_set = RED_PIECES if color == RED else BLACK_PIECES
        
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                if piece and piece in target_set:
                    pieces.append((row, col, piece))
        
        return pieces
    
    def __str__(self) -> str:
        """Return string representation of the board for debugging."""
        lines = ["  0 1 2 3 4 5 6 7 8"]
        for row in range(BOARD_ROWS - 1, -1, -1):
            line = f"{row} "
            for col in range(BOARD_COLS):
                piece = self.board[row][col]
                line += (piece if piece else '.') + ' '
            lines.append(line)
        return '\n'.join(lines)
