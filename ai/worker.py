"""QThread worker for AI computation.

This module provides a threaded worker for running AI calculations
without blocking the main UI thread.

Typical usage example:
    worker = AIWorker(board, mode='AI_MOVE', difficulty='中级')
    worker.move_ready.connect(on_move_ready)
    worker.start()
"""

from PySide6.QtCore import QThread, Signal

from ai.search import get_best_move
from core.board import Board


class AIWorker(QThread):
    """AI computation worker thread.

    Runs AI move calculation in a separate thread to keep the UI responsive.

    Attributes:
        board: Copy of the board state for calculation.
        mode: Operation mode ('AI_MOVE' or 'HINT').
        difficulty: AI difficulty level.

    Signals:
        move_ready: Emitted when AI move is calculated (from_pos, to_pos).
        hint_ready: Emitted when hint is calculated (from_pos, to_pos).
        error_occurred: Emitted when an error occurs (error_message).
    """

    move_ready = Signal(tuple, tuple)
    hint_ready = Signal(tuple, tuple)
    error_occurred = Signal(str)

    def __init__(
        self, board: Board, mode: str = 'AI_MOVE', difficulty: str = '中级'
    ) -> None:
        """Initialize the AI worker thread.

        Args:
            board: The board state to analyze.
            mode: Operation mode ('AI_MOVE' or 'HINT').
            difficulty: AI difficulty level.
        """
        super().__init__()
        self.board = board.copy()
        self.mode = mode
        self.difficulty = difficulty
        self._is_running = True

    def run(self) -> None:
        """Execute the AI calculation in the thread."""
        try:
            best_move = get_best_move(self.board, self.difficulty)

            if not self._is_running:
                return

            if best_move:
                from_pos, to_pos = best_move
                if self.mode == 'AI_MOVE':
                    self.move_ready.emit(from_pos, to_pos)
                elif self.mode == 'HINT':
                    self.hint_ready.emit(from_pos, to_pos)
            else:
                self.error_occurred.emit("无法找到合法移动")

        except Exception as e:
            self.error_occurred.emit(f"AI计算错误: {str(e)}")

    def stop(self) -> None:
        """Stop the worker thread."""
        self._is_running = False
