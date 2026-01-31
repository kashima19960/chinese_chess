"""Board view with graphics scene for Chinese Chess.

This module provides the main chess board visualization using PySide6's
QGraphicsView framework. It handles board rendering, piece placement,
user interaction, and move animations.

Typical usage example:
    board = Board(INITIAL_FEN)
    view = BoardView(board)
    view.piece_clicked.connect(handle_click)
"""

from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import (
    Signal,
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    Qt,
)
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
)

from core.board import Board
from core.constants import BOARD_COLS, BOARD_ROWS
from ui.pieces import PieceItem
from ui.styles import Colors


class BoardView(QGraphicsView):
    """A graphical view of the Chinese Chess board.
    
    This class handles all visual aspects of the chess board including:
    - Board grid and decoration rendering
    - Piece placement and updates
    - User click interactions
    - Move animations
    - Visual feedback (selection, legal moves, hints)
    
    Signals:
        piece_clicked: Emitted when a board position is clicked.
            Args: (row: int, col: int)
        move_made: Emitted when a move animation completes.
            Args: (from_pos: tuple, to_pos: tuple)
    
    Attributes:
        board: The Board object representing the game state.
        cell_size: Size of each cell in pixels.
        is_locked: Whether user interaction is disabled.
    """
    
    # Qt Signals
    piece_clicked = Signal(int, int)
    move_made = Signal(tuple, tuple)
    
    def __init__(self, board: Board, cell_size: float = 60.0) -> None:
        """Initialize the board view.
        
        Args:
            board: The Board object to visualize.
            cell_size: Size of each board cell in pixels.
        """
        super().__init__()
        
        self.board = board
        self.cell_size = cell_size
        self._margin = cell_size
        
        # Create graphics scene
        self._scene = QGraphicsScene()
        self.setScene(self._scene)
        
        # Configure view rendering
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Set background color
        self.setStyleSheet(f"background-color: {Colors.BACKGROUND};")
        
        # Interaction state
        self.selected_piece: Optional[PieceItem] = None
        self.selected_pos: Optional[Tuple[int, int]] = None
        self.is_locked = False
        
        # Visual markers
        self._hint_markers: List[QGraphicsEllipseItem] = []
        self._legal_move_markers: List[QGraphicsEllipseItem] = []
        
        # Piece items indexed by position
        self._piece_items: Dict[Tuple[int, int], PieceItem] = {}
        
        # Current animation reference
        self._current_animation: Optional[QPropertyAnimation] = None
        
        # Draw board and pieces
        self._draw_board()
        self._draw_pieces()
        
        # Set scene size
        scene_width = self._margin * 2 + (BOARD_COLS - 1) * self.cell_size
        scene_height = self._margin * 2 + (BOARD_ROWS - 1) * self.cell_size
        self.setSceneRect(0, 0, scene_width, scene_height)
        self.setFixedSize(int(scene_width) + 20, int(scene_height) + 20)
    
    def _draw_board(self) -> None:
        """Draw the chess board background and grid lines."""
        board_width = self._margin * 2 + (BOARD_COLS - 1) * self.cell_size
        board_height = self._margin * 2 + (BOARD_ROWS - 1) * self.cell_size
        
        # Draw board background with warm wood color
        bg_rect = QGraphicsRectItem(0, 0, board_width, board_height)
        bg_rect.setBrush(QBrush(QColor(Colors.BOARD_BG)))
        bg_rect.setPen(QPen(Qt.NoPen))
        bg_rect.setZValue(0)
        self._scene.addItem(bg_rect)
        
        # Draw grid lines
        line_pen = QPen(QColor(Colors.BOARD_LINE), 2)
        
        # Horizontal lines
        for row in range(BOARD_ROWS):
            y = self._margin + row * self.cell_size
            line = QGraphicsLineItem(
                self._margin, y,
                self._margin + (BOARD_COLS - 1) * self.cell_size, y
            )
            line.setPen(line_pen)
            line.setZValue(1)
            self._scene.addItem(line)
        
        # Vertical lines (split by river)
        for col in range(BOARD_COLS):
            x = self._margin + col * self.cell_size
            
            # Red side (bottom half)
            line1 = QGraphicsLineItem(
                x, self._margin,
                x, self._margin + 4 * self.cell_size
            )
            line1.setPen(line_pen)
            line1.setZValue(1)
            self._scene.addItem(line1)
            
            # Black side (top half)
            line2 = QGraphicsLineItem(
                x, self._margin + 5 * self.cell_size,
                x, self._margin + 9 * self.cell_size
            )
            line2.setPen(line_pen)
            line2.setZValue(1)
            self._scene.addItem(line2)
        
        # Draw palace diagonal lines
        self._draw_palace_lines(line_pen)
    
    def _draw_palace_lines(self, pen: QPen) -> None:
        """Draw the diagonal lines in both palaces.
        
        Args:
            pen: The QPen to use for drawing.
        """
        # Red palace (bottom)
        x1 = self._margin + 3 * self.cell_size
        x2 = self._margin + 5 * self.cell_size
        y1 = self._margin + 0 * self.cell_size
        y2 = self._margin + 2 * self.cell_size
        
        line1 = QGraphicsLineItem(x1, y1, x2, y2)
        line1.setPen(pen)
        line1.setZValue(1)
        self._scene.addItem(line1)
        
        line2 = QGraphicsLineItem(x2, y1, x1, y2)
        line2.setPen(pen)
        line2.setZValue(1)
        self._scene.addItem(line2)
        
        # Black palace (top)
        y1 = self._margin + 7 * self.cell_size
        y2 = self._margin + 9 * self.cell_size
        
        line3 = QGraphicsLineItem(x1, y1, x2, y2)
        line3.setPen(pen)
        line3.setZValue(1)
        self._scene.addItem(line3)
        
        line4 = QGraphicsLineItem(x2, y1, x1, y2)
        line4.setPen(pen)
        line4.setZValue(1)
        self._scene.addItem(line4)
    
    def _draw_pieces(self) -> None:
        """Draw all pieces on the board from current game state."""
        self._piece_items.clear()
        
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board.get_piece(row, col)
                if piece:
                    self._add_piece_item(piece, row, col)
    
    def _add_piece_item(self, piece: str, row: int, col: int) -> None:
        """Add a piece item to the scene.
        
        Args:
            piece: The piece type character.
            row: Board row position.
            col: Board column position.
        """
        piece_item = PieceItem(piece, row, col, self.cell_size)
        x, y = self._board_to_scene(row, col)
        piece_item.setPos(x, y)
        
        self._scene.addItem(piece_item)
        self._piece_items[(row, col)] = piece_item
    
    def _board_to_scene(self, row: int, col: int) -> Tuple[float, float]:
        """Convert board coordinates to scene coordinates.
        
        Args:
            row: Board row (0-9, 0 at bottom).
            col: Board column (0-8, 0 at left).
        
        Returns:
            Tuple of (x, y) scene coordinates.
        """
        x = self._margin + col * self.cell_size
        # Y-axis is inverted (row 0 at bottom of screen)
        y = self._margin + (BOARD_ROWS - 1 - row) * self.cell_size
        return x, y
    
    def _scene_to_board(
        self, x: float, y: float
    ) -> Optional[Tuple[int, int]]:
        """Convert scene coordinates to board coordinates.
        
        Args:
            x: Scene x coordinate.
            y: Scene y coordinate.
        
        Returns:
            Tuple of (row, col) if valid, None otherwise.
        """
        col = round((x - self._margin) / self.cell_size)
        row = BOARD_ROWS - 1 - round((y - self._margin) / self.cell_size)
        
        if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS:
            return row, col
        return None
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse press events for piece selection.
        
        Args:
            event: The mouse event.
        """
        if self.is_locked:
            return
        
        scene_pos = self.mapToScene(event.pos())
        board_pos = self._scene_to_board(scene_pos.x(), scene_pos.y())
        
        if board_pos:
            row, col = board_pos
            self.piece_clicked.emit(row, col)
    
    def select_piece(
        self,
        row: int,
        col: int,
        legal_moves: List[Tuple[int, int]]
    ) -> None:
        """Select a piece and show its legal moves.
        
        Args:
            row: Row of the piece to select.
            col: Column of the piece to select.
            legal_moves: List of legal move destinations.
        """
        self.clear_selection()
        
        if (row, col) in self._piece_items:
            piece_item = self._piece_items[(row, col)]
            piece_item.set_selected(True)
            self.selected_piece = piece_item
            self.selected_pos = (row, col)
        
        self._show_legal_moves(legal_moves)
    
    def clear_selection(self) -> None:
        """Clear the current piece selection and markers."""
        if self.selected_piece:
            self.selected_piece.set_selected(False)
            self.selected_piece = None
            self.selected_pos = None
        
        self._clear_legal_moves()
    
    def _show_legal_moves(self, legal_moves: List[Tuple[int, int]]) -> None:
        """Display markers for legal move destinations.
        
        Args:
            legal_moves: List of (row, col) positions that are legal moves.
        """
        self._clear_legal_moves()
        
        for row, col in legal_moves:
            x, y = self._board_to_scene(row, col)
            has_piece = (row, col) in self._piece_items
            
            if has_piece:
                # Capture indicator - larger red circle
                marker = QGraphicsEllipseItem(x - 25, y - 25, 50, 50)
                marker.setPen(QPen(QColor(Colors.CAPTURE_HINT), 3))
                marker.setBrush(QBrush(Qt.NoBrush))
            else:
                # Move indicator - small green dot
                marker = QGraphicsEllipseItem(x - 8, y - 8, 16, 16)
                marker.setPen(QPen(Qt.NoPen))
                marker.setBrush(QBrush(QColor(Colors.LEGAL_MOVE)))
            
            marker.setZValue(5)
            self._scene.addItem(marker)
            self._legal_move_markers.append(marker)
    
    def _clear_legal_moves(self) -> None:
        """Remove all legal move markers from the scene."""
        for marker in self._legal_move_markers:
            self._scene.removeItem(marker)
        self._legal_move_markers.clear()
    
    def show_hint(
        self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> None:
        """Display hint markers for a suggested move.
        
        Args:
            from_pos: Starting position (row, col).
            to_pos: Destination position (row, col).
        """
        self.clear_hint()
        
        for pos in [from_pos, to_pos]:
            row, col = pos
            x, y = self._board_to_scene(row, col)
            
            marker = QGraphicsEllipseItem(x - 30, y - 30, 60, 60)
            marker.setPen(QPen(QColor(Colors.HINT_MARKER), 4))
            marker.setBrush(QBrush(Qt.NoBrush))
            marker.setZValue(5)
            self._scene.addItem(marker)
            self._hint_markers.append(marker)
    
    def clear_hint(self) -> None:
        """Remove all hint markers from the scene."""
        for marker in self._hint_markers:
            self._scene.removeItem(marker)
        self._hint_markers.clear()
    
    def animate_move(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        captured_piece: Optional[str] = None
    ) -> None:
        """Animate a piece moving from one position to another.
        
        Args:
            from_pos: Starting position (row, col).
            to_pos: Destination position (row, col).
            captured_piece: The piece being captured (if any).
        """
        r1, c1 = from_pos
        r2, c2 = to_pos
        
        if (r1, c1) not in self._piece_items:
            return
        
        piece_item = self._piece_items[(r1, c1)]
        
        # Remove captured piece if present
        if (r2, c2) in self._piece_items:
            captured_item = self._piece_items.pop((r2, c2))
            self._scene.removeItem(captured_item)
        
        # Create smooth move animation
        start_pos = piece_item.pos()
        end_x, end_y = self._board_to_scene(r2, c2)
        end_pos = QPointF(end_x, end_y)
        
        animation = QPropertyAnimation(piece_item, b"pos")
        animation.setDuration(300)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        def on_animation_finished():
            self._piece_items.pop((r1, c1), None)
            self._piece_items[(r2, c2)] = piece_item
            piece_item.update_position(r2, c2)
            self.move_made.emit(from_pos, to_pos)
        
        animation.finished.connect(on_animation_finished)
        animation.start()
        
        self._current_animation = animation
    
    def refresh_board(self) -> None:
        """Refresh the board display from current game state."""
        # Remove all existing pieces
        for piece_item in self._piece_items.values():
            self._scene.removeItem(piece_item)
        
        # Redraw pieces
        self._draw_pieces()
        self.clear_selection()
        self.clear_hint()
    
    def set_locked(self, locked: bool) -> None:
        """Set whether user interaction is locked.
        
        Args:
            locked: True to disable interaction, False to enable.
        """
        self.is_locked = locked
        
        if locked:
            self.clear_selection()
            self.clear_hint()
