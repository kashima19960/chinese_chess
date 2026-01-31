"""Chess piece graphics items for the board view.

This module provides the graphical representation of chess pieces using
PySide6's QGraphicsObject. Each piece is rendered as a circular item with
Chinese character text.

Typical usage example:
    piece = PieceItem('R', 0, 0, 60.0)
    scene.addItem(piece)
"""

from PySide6.QtCore import QRectF
from PySide6.QtGui import QBrush, QColor, QFont, QPen
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsObject,
    QGraphicsTextItem,
)

from core.constants import PIECE_CHINESE_NAMES, RED, get_piece_color
from ui.styles import Colors, Fonts


class PieceItem(QGraphicsObject):
    """A graphical chess piece item.
    
    This class represents a single chess piece on the board. It handles
    rendering the piece with proper colors based on the player (red/black)
    and provides selection highlighting functionality.
    
    Attributes:
        piece: The piece type character (e.g., 'R' for red rook).
        board_row: The current row position on the board.
        board_col: The current column position on the board.
        is_selected: Whether the piece is currently selected.
    """
    
    def __init__(
        self,
        piece: str,
        row: int,
        col: int,
        cell_size: float
    ) -> None:
        """Initialize a chess piece item.
        
        Args:
            piece: The piece type character (e.g., 'R', 'n', 'K').
            row: The initial row position (0-9).
            col: The initial column position (0-8).
            cell_size: The size of each board cell in pixels.
        """
        super().__init__()
        
        self.piece = piece
        self.board_row = row
        self.board_col = col
        self.cell_size = cell_size
        self.radius = cell_size * 0.42
        self.is_selected = False
        
        # Create the circular background
        self._ellipse = QGraphicsEllipseItem(
            -self.radius, -self.radius,
            self.radius * 2, self.radius * 2,
            self
        )
        
        # Create the text label
        self._text_item = QGraphicsTextItem(
            PIECE_CHINESE_NAMES[piece], self
        )
        
        # Setup visual appearance
        self._setup_appearance()
        self._setup_text()
        
        # Enable selection interaction
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setZValue(10)  # Ensure pieces render above board
    
    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle of the piece.
        
        Returns:
            A QRectF representing the piece's bounds.
        """
        return QRectF(
            -self.radius, -self.radius,
            self.radius * 2, self.radius * 2
        )
    
    def paint(self, painter, option, widget) -> None:
        """Paint the piece (handled by child items)."""
        # Actual rendering is done by child QGraphicsItems
        pass
    
    def _setup_appearance(self) -> None:
        """Configure the piece's visual appearance based on its color."""
        color = get_piece_color(self.piece)
        
        if color == RED:
            bg_color = QColor(Colors.RED_PIECE_BG)
            border_color = QColor(Colors.RED_PIECE_BORDER)
        else:
            bg_color = QColor(Colors.BLACK_PIECE_BG)
            border_color = QColor(Colors.BLACK_PIECE_BORDER)
        
        self._ellipse.setBrush(QBrush(bg_color))
        self._ellipse.setPen(QPen(border_color, 2))
        
        # Store normal pen for reset after selection
        self._normal_pen = QPen(border_color, 2)
    
    def _setup_text(self) -> None:
        """Configure the piece's text label styling."""
        color = get_piece_color(self.piece)
        
        if color == RED:
            text_color = QColor(Colors.RED_PIECE_TEXT)
        else:
            text_color = QColor(Colors.BLACK_PIECE_TEXT)
        
        self._text_item.setDefaultTextColor(text_color)
        
        # Set font with appropriate size
        font_size = int(self.cell_size * 0.32)
        font = QFont(Fonts.PRIMARY, font_size, QFont.Bold)
        self._text_item.setFont(font)
        
        # Center the text within the piece
        text_rect = self._text_item.boundingRect()
        self._text_item.setPos(
            -text_rect.width() / 2,
            -text_rect.height() / 2
        )
    
    def set_selected(self, selected: bool) -> None:
        """Set the selection state of the piece.
        
        Args:
            selected: True to select the piece, False to deselect.
        """
        self.is_selected = selected
        
        if selected:
            # Show golden highlight when selected
            highlight_pen = QPen(QColor(Colors.SELECTED), 4)
            self._ellipse.setPen(highlight_pen)
        else:
            # Restore normal border
            self._ellipse.setPen(self._normal_pen)
    
    def update_position(self, row: int, col: int) -> None:
        """Update the piece's logical board position.
        
        This method updates the stored board coordinates after a move
        animation completes. It does not move the visual position.
        
        Args:
            row: The new row position.
            col: The new column position.
        """
        self.board_row = row
        self.board_col = col
