"""Main application window for Chinese Chess.

This is the main entry point for the Chinese Chess application. It creates
the main window, manages game state, and coordinates between the UI
components and game logic.

Typical usage example:
    python main.py
"""

import logging
import os
import sys
import warnings

# Suppress Qt warnings before importing PySide6
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.fonts=false'

from PySide6.QtCore import QDir, QPoint, Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# PySide6 automatically supports High DPI scaling

from ai.worker import AIWorker
from core.board import Board
from core.constants import BLACK, INITIAL_FEN, RED, get_piece_color
from core.notation import NotationGenerator
from core.rules import RuleEngine
from ui.board_view import BoardView
from ui.control_panel import ControlPanel
from ui.styles import Colors, Fonts, StyleSheets


class TitleBar(QWidget):
    """Custom title bar for frameless window.
    
    Provides window controls (minimize, maximize, close) and allows
    dragging the window by the title bar area.
    
    Attributes:
        parent: The parent MainWindow instance.
    """
    
    def __init__(self, parent: QMainWindow) -> None:
        """Initialize the title bar.
        
        Args:
            parent: The parent MainWindow.
        """
        super().__init__(parent)
        self._parent = parent
        self._pressing = False
        self._start_pos = None
        
        self.setFixedHeight(44)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the title bar UI components."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.PRIMARY};
            }}
            QLabel {{
                color: {Colors.SURFACE};
                font-weight: bold;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {Colors.SURFACE};
                font-size: 16px;
                padding: 4px 12px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.2);
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(8)
        
        # Title label
        title_label = QLabel("中国象棋")
        title_label.setFont(QFont(Fonts.PRIMARY, 14, QFont.Bold))
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Minimize button
        self._min_btn = QPushButton("—")
        self._min_btn.setFixedSize(44, 36)
        self._min_btn.setCursor(Qt.PointingHandCursor)
        self._min_btn.clicked.connect(self._parent.showMinimized)
        layout.addWidget(self._min_btn)
        
        # Maximize/restore button
        self._max_btn = QPushButton("□")
        self._max_btn.setFixedSize(44, 36)
        self._max_btn.setCursor(Qt.PointingHandCursor)
        self._max_btn.clicked.connect(self._toggle_maximize)
        layout.addWidget(self._max_btn)
        
        # Close button
        self._close_btn = QPushButton("×")
        self._close_btn.setFixedSize(44, 36)
        self._close_btn.setCursor(Qt.PointingHandCursor)
        self._close_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: rgba(244, 67, 54, 0.9);
            }
        """)
        self._close_btn.clicked.connect(self._parent.close)
        layout.addWidget(self._close_btn)
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse press for window dragging."""
        if event.button() == Qt.LeftButton:
            self._pressing = True
            self._start_pos = (
                event.globalPos() - self._parent.frameGeometry().topLeft()
            )
    
    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move for window dragging."""
        if self._pressing and self._start_pos:
            self._parent.move(event.globalPos() - self._start_pos)
    
    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release to stop dragging."""
        self._pressing = False
        self._start_pos = None
    
    def mouseDoubleClickEvent(self, event) -> None:
        """Handle double-click to toggle maximize."""
        self._toggle_maximize()
    
    def _toggle_maximize(self) -> None:
        """Toggle between maximized and normal window state."""
        if self._parent.isMaximized():
            self._parent.showNormal()
            self._max_btn.setText("□")
        else:
            self._parent.showMaximized()
            self._max_btn.setText("❐")


class MainWindow(QMainWindow):
    """Main application window for Chinese Chess.
    
    This window manages the overall game including:
    - Game state (board, rules, history)
    - UI components (board view, control panel)
    - AI worker thread
    - State machine for game flow
    
    Attributes:
        board: The current game board state.
        game_mode: "PVE" or "PVP".
        difficulty: Current AI difficulty level.
        player_color: The human player's color in PVE mode.
        game_active: Whether a game is currently in progress.
        state: Current state machine state.
    """
    
    # Game states
    STATE_IDLE = "IDLE"
    STATE_USER_TURN = "USER_TURN"
    STATE_AI_THINKING = "AI_THINKING"
    STATE_HINT_CALCULATING = "HINT_CALCULATING"
    STATE_GAME_OVER = "GAME_OVER"
    
    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()
        
        # Initialize game state
        self.board = Board(INITIAL_FEN)
        self._rule_engine = RuleEngine(self.board)
        self._notation_gen = NotationGenerator(self.board)
        
        # Game settings
        self.game_mode = "PVE"
        self.difficulty = "中级"
        self.player_color = RED
        self.game_active = False
        
        # AI worker
        self._ai_worker: AIWorker = None
        
        # State machine
        self.state = self.STATE_IDLE
        
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("中国象棋")
        
        # Configure frameless window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Apply main window style
        self.setStyleSheet(StyleSheets.main_window())
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main vertical layout (title bar + content)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add custom title bar
        self._title_bar = TitleBar(self)
        main_layout.addWidget(self._title_bar)
        
        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {Colors.BACKGROUND};")
        main_layout.addWidget(content_widget)
        
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(24)
        
        # Board view
        self._board_view = BoardView(self.board)
        self._board_view.piece_clicked.connect(self._on_piece_clicked)
        self._board_view.move_made.connect(self._on_move_made)
        content_layout.addWidget(self._board_view)
        
        # Control panel
        self._control_panel = ControlPanel()
        self._control_panel.start_game_clicked.connect(self._start_game)
        self._control_panel.undo_clicked.connect(self._undo_move)
        self._control_panel.hint_clicked.connect(self._request_hint)
        self._control_panel.resign_clicked.connect(self._resign_game)
        content_layout.addWidget(self._control_panel)
        
        # Set minimum window size
        self.setMinimumSize(1100, 780)
    
    def _start_game(self) -> None:
        """Start a new game with current settings."""
        # Get settings from control panel
        settings = self._control_panel.get_settings()
        self.game_mode, self.difficulty, player_color_str = settings
        self.player_color = RED if player_color_str == "RED" else BLACK
        
        # Reset game state
        self.board = Board(INITIAL_FEN)
        self._rule_engine = RuleEngine(self.board)
        self._notation_gen = NotationGenerator(self.board)
        
        # Refresh UI
        self._board_view.board = self.board
        self._board_view.refresh_board()
        self._control_panel.clear_notation()
        
        # Set game active
        self.game_active = True
        self._control_panel.set_game_active(True)
        
        # Set initial state based on mode
        if self.game_mode == "PVP":
            self.state = self.STATE_USER_TURN
            self._control_panel.set_status("红方走棋", "red")
            self._board_view.set_locked(False)
        else:  # PVE
            if self.player_color == RED:
                self.state = self.STATE_USER_TURN
                self._control_panel.set_status("轮到你走棋(红方)", "red")
                self._board_view.set_locked(False)
            else:
                self.state = self.STATE_AI_THINKING
                self._control_panel.set_status("AI思考中...", "orange")
                self._board_view.set_locked(True)
                self._request_ai_move()
    
    def _on_piece_clicked(self, row: int, col: int) -> None:
        """Handle piece click events.
        
        Args:
            row: Row of the clicked position.
            col: Column of the clicked position.
        """
        if self.state != self.STATE_USER_TURN:
            return
        
        piece = self.board.get_piece(row, col)
        
        # Check if a piece is already selected
        if self._board_view.selected_pos:
            from_pos = self._board_view.selected_pos
            
            # Check if clicked position is a legal move
            legal_moves = self._rule_engine.get_legal_moves(
                from_pos[0], from_pos[1]
            )
            if (row, col) in legal_moves:
                self._make_move(from_pos, (row, col))
                return
            
            # Clear selection if clicking elsewhere
            self._board_view.clear_selection()
        
        # Select a new piece if it belongs to current player
        if piece and get_piece_color(piece) == self.board.current_player:
            # Allow selection if PVP or player's turn in PVE
            if (self.game_mode == "PVP" or 
                    self.board.current_player == self.player_color):
                legal_moves = self._rule_engine.get_legal_moves(row, col)
                if legal_moves:
                    self._board_view.select_piece(row, col, legal_moves)
    
    def _make_move(self, from_pos: tuple, to_pos: tuple) -> None:
        """Execute a move on the board.
        
        Args:
            from_pos: Starting position (row, col).
            to_pos: Destination position (row, col).
        """
        # Generate notation before move
        notation = self._notation_gen.generate_notation(from_pos, to_pos)
        
        # Execute move
        captured = self.board.move_piece(from_pos, to_pos)
        
        # Animate the move
        self._board_view.animate_move(from_pos, to_pos, captured)
        
        # Add notation to history
        self._control_panel.add_notation(notation)
        
        # Clear visual feedback
        self._board_view.clear_selection()
        self._board_view.clear_hint()
    
    def _on_move_made(self, from_pos: tuple, to_pos: tuple) -> None:
        """Handle move completion (after animation).
        
        Args:
            from_pos: Starting position (row, col).
            to_pos: Destination position (row, col).
        """
        # Update rule engine
        self._rule_engine = RuleEngine(self.board)
        self._notation_gen = NotationGenerator(self.board)
        
        # Check for game over
        result = self._rule_engine.get_game_result()
        if result is not None:
            self._end_game(result)
            return
        
        # Transition to next state
        if self.game_mode == "PVP":
            self.state = self.STATE_USER_TURN
            color_name = "红方" if self.board.current_player == RED else "黑方"
            color = "red" if self.board.current_player == RED else "black"
            self._control_panel.set_status(f"{color_name}走棋", color)
        else:  # PVE
            if self.board.current_player == self.player_color:
                self.state = self.STATE_USER_TURN
                self._control_panel.set_status("轮到你走棋", "green")
                self._board_view.set_locked(False)
            else:
                self.state = self.STATE_AI_THINKING
                self._control_panel.set_status("AI思考中...", "orange")
                self._control_panel.show_thinking(True)
                self._board_view.set_locked(True)
                self._request_ai_move()
    
    def _request_ai_move(self) -> None:
        """Request the AI to make a move."""
        if self._ai_worker and self._ai_worker.isRunning():
            self._ai_worker.stop()
            self._ai_worker.wait()
        
        self._ai_worker = AIWorker(
            self.board,
            mode='AI_MOVE',
            difficulty=self.difficulty
        )
        self._ai_worker.move_ready.connect(self._on_ai_move_ready)
        self._ai_worker.error_occurred.connect(self._on_ai_error)
        self._ai_worker.start()
    
    def _on_ai_move_ready(self, from_pos: tuple, to_pos: tuple) -> None:
        """Handle AI move completion.
        
        Args:
            from_pos: Starting position (row, col).
            to_pos: Destination position (row, col).
        """
        self._control_panel.show_thinking(False)
        self._make_move(from_pos, to_pos)
    
    def _request_hint(self) -> None:
        """Request a hint from the AI."""
        if self.state != self.STATE_USER_TURN:
            return
        
        if self._ai_worker and self._ai_worker.isRunning():
            return
        
        self.state = self.STATE_HINT_CALCULATING
        self._control_panel.set_status("计算提示中...", "orange")
        self._control_panel.show_thinking(True)
        self._board_view.set_locked(True)
        
        self._ai_worker = AIWorker(
            self.board,
            mode='HINT',
            difficulty=self.difficulty
        )
        self._ai_worker.hint_ready.connect(self._on_hint_ready)
        self._ai_worker.error_occurred.connect(self._on_ai_error)
        self._ai_worker.start()
    
    def _on_hint_ready(self, from_pos: tuple, to_pos: tuple) -> None:
        """Handle hint calculation completion.
        
        Args:
            from_pos: Suggested starting position (row, col).
            to_pos: Suggested destination position (row, col).
        """
        self._control_panel.show_thinking(False)
        self.state = self.STATE_USER_TURN
        self._control_panel.set_status("建议走法已显示", "blue")
        self._board_view.set_locked(False)
        self._board_view.show_hint(from_pos, to_pos)
    
    def _on_ai_error(self, error_msg: str) -> None:
        """Handle AI errors.
        
        Args:
            error_msg: The error message.
        """
        self._control_panel.show_thinking(False)
        QMessageBox.warning(self, "错误", error_msg)
        
        if self.state == self.STATE_AI_THINKING:
            # AI cannot move, player wins
            self._end_game(self.player_color)
        else:
            self.state = self.STATE_USER_TURN
            self._board_view.set_locked(False)
    
    def _undo_move(self) -> None:
        """Undo the last move(s)."""
        if not self.game_active:
            return
        
        # In PVE, undo both player and AI moves
        if self.game_mode == "PVE":
            if len(self.board.history) >= 2:
                self.board.undo_move()
                self.board.undo_move()
            elif len(self.board.history) == 1:
                self.board.undo_move()
        else:  # PVP, undo one move
            if self.board.history:
                self.board.undo_move()
        
        # Refresh display
        self._board_view.board = self.board
        self._board_view.refresh_board()
        self._rule_engine = RuleEngine(self.board)
        self._notation_gen = NotationGenerator(self.board)
        
        # Remove notation entries
        count = self._control_panel.notation_list.count()
        if count > 0:
            if self.game_mode == "PVE" and count >= 2:
                self._control_panel.notation_list.takeItem(count - 1)
                self._control_panel.notation_list.takeItem(count - 2)
            else:
                self._control_panel.notation_list.takeItem(count - 1)
        
        # Restore player turn
        self.state = self.STATE_USER_TURN
        self._board_view.set_locked(False)
        self._control_panel.set_status("已悔棋", "blue")
    
    def _resign_game(self) -> None:
        """Handle player resignation."""
        if not self.game_active:
            return
        
        reply = QMessageBox.question(
            self, "确认", "确定要认输吗?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            winner = -self.board.current_player
            self._end_game(winner)
    
    def _end_game(self, winner: int) -> None:
        """End the game and display results.
        
        Args:
            winner: The winning player (RED or BLACK).
        """
        self.game_active = False
        self.state = self.STATE_GAME_OVER
        self._board_view.set_locked(True)
        self._control_panel.set_game_active(False)
        
        if winner == RED:
            winner_name = "红方"
            color = "red"
        else:
            winner_name = "黑方"
            color = "black"
        
        self._control_panel.set_status(f"游戏结束 - {winner_name}获胜!", color)
        QMessageBox.information(self, "游戏结束", f"{winner_name}获胜!")
    
    def closeEvent(self, event) -> None:
        """Handle window close event.
        
        Args:
            event: The close event.
        """
        if self._ai_worker and self._ai_worker.isRunning():
            self._ai_worker.stop()
            self._ai_worker.wait()
        event.accept()


def main() -> None:
    """Main entry point for the application."""
    # Suppress warnings
    warnings.filterwarnings('ignore')
    logging.getLogger().setLevel(logging.CRITICAL)
    
    app = QApplication(sys.argv)
    
    # Set resource search path
    resource_path = os.path.join(os.path.dirname(__file__), 'resources')
    if os.path.exists(resource_path):
        QDir.addSearchPath('icon', os.path.join(resource_path, 'icon'))
    
    # Set application icon
    icon_path = os.path.join(resource_path, 'app_icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
