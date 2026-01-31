"""Control panel for game settings and actions.

This module provides the control panel widget that allows users to configure
game settings (mode, difficulty, color) and perform game actions (start,
undo, hint, resign).

Typical usage example:
    panel = ControlPanel()
    panel.start_game_clicked.connect(start_game_handler)
"""

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from ui.styles import Colors, Fonts, StyleSheets


class ControlPanel(QWidget):
    """Control panel widget for game settings and actions.
    
    This panel provides UI controls for:
    - Game mode selection (PVE/PVP)
    - Difficulty level selection
    - Player color selection
    - Game action buttons (start, undo, hint, resign)
    - Game status display
    - Move notation history
    
    Signals:
        start_game_clicked: Emitted when start game button is clicked.
        undo_clicked: Emitted when undo button is clicked.
        hint_clicked: Emitted when hint button is clicked.
        resign_clicked: Emitted when resign button is clicked.
        settings_changed: Emitted when any setting changes.
            Args: (mode: str, difficulty: str, player_color: str)
    """
    
    # Qt Signals
    start_game_clicked = Signal()
    undo_clicked = Signal()
    hint_clicked = Signal()
    resign_clicked = Signal()
    settings_changed = Signal(str, str, str)
    
    def __init__(self) -> None:
        """Initialize the control panel."""
        super().__init__()
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize the user interface components."""
        # Apply stylesheet
        self.setStyleSheet(StyleSheets.control_panel())
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title_label = QLabel("中国象棋")
        title_label.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_TITLE, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {Colors.PRIMARY};")
        layout.addWidget(title_label)
        
        # Settings group
        settings_group = self._create_settings_group()
        layout.addWidget(settings_group)
        
        # Actions group
        actions_group = self._create_actions_group()
        layout.addWidget(actions_group)
        
        # Progress bar (shown during AI thinking)
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 0)  # Indeterminate progress
        self._progress_bar.setVisible(False)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(8)
        layout.addWidget(self._progress_bar)
        
        # Status label
        self._status_label = QLabel("请点击开始游戏")
        self._status_label.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_BODY))
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setStyleSheet(StyleSheets.status_label("blue"))
        layout.addWidget(self._status_label)
        
        # Notation history
        notation_label = QLabel("棋谱记录:")
        notation_label.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_HEADING, QFont.Bold))
        layout.addWidget(notation_label)
        
        self._notation_list = QListWidget()
        self._notation_list.setFont(QFont(Fonts.SECONDARY, Fonts.SIZE_BODY))
        self._notation_list.setMaximumHeight(280)
        layout.addWidget(self._notation_list)
        
        # Stretch to push content up
        layout.addStretch()
        
        self.setLayout(layout)
        self.setFixedWidth(320)
    
    def _create_settings_group(self) -> QGroupBox:
        """Create the game settings group box.
        
        Returns:
            A QGroupBox containing all game settings controls.
        """
        group = QGroupBox("游戏设置")
        group.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_BODY, QFont.Bold))
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Game mode selection
        mode_label = QLabel("游戏模式:")
        layout.addWidget(mode_label)
        
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["人机对战", "人人对战"])
        self._mode_combo.currentTextChanged.connect(self._on_mode_changed)
        layout.addWidget(self._mode_combo)
        
        # Difficulty selection
        self._difficulty_label = QLabel("难度等级:")
        layout.addWidget(self._difficulty_label)
        
        self._difficulty_combo = QComboBox()
        self._difficulty_combo.addItems(["小白", "初级", "中级", "高级", "大师"])
        self._difficulty_combo.setCurrentText("中级")
        layout.addWidget(self._difficulty_combo)
        
        # Player color selection
        self._color_label = QLabel("执子选择:")
        layout.addWidget(self._color_label)
        
        color_layout = QHBoxLayout()
        self._color_button_group = QButtonGroup()
        
        self._red_radio = QRadioButton("执红(先手)")
        self._red_radio.setChecked(True)
        self._color_button_group.addButton(self._red_radio)
        color_layout.addWidget(self._red_radio)
        
        self._black_radio = QRadioButton("执黑(后手)")
        self._color_button_group.addButton(self._black_radio)
        color_layout.addWidget(self._black_radio)
        
        layout.addLayout(color_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_actions_group(self) -> QGroupBox:
        """Create the game actions group box.
        
        Returns:
            A QGroupBox containing all action buttons.
        """
        group = QGroupBox("游戏操作")
        group.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_BODY, QFont.Bold))
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Start game button
        self._start_button = QPushButton("开始游戏")
        self._start_button.setFont(QFont(Fonts.PRIMARY, Fonts.SIZE_HEADING))
        self._start_button.setMinimumHeight(44)
        self._start_button.setCursor(Qt.PointingHandCursor)
        self._start_button.clicked.connect(self.start_game_clicked.emit)
        layout.addWidget(self._start_button)
        
        # Other action buttons (disabled by default)
        self._undo_button = QPushButton("悔棋")
        self._undo_button.setEnabled(False)
        self._undo_button.setCursor(Qt.PointingHandCursor)
        self._undo_button.clicked.connect(self.undo_clicked.emit)
        layout.addWidget(self._undo_button)
        
        self._hint_button = QPushButton("智能提示")
        self._hint_button.setEnabled(False)
        self._hint_button.setCursor(Qt.PointingHandCursor)
        self._hint_button.clicked.connect(self.hint_clicked.emit)
        layout.addWidget(self._hint_button)
        
        self._resign_button = QPushButton("认输")
        self._resign_button.setEnabled(False)
        self._resign_button.setCursor(Qt.PointingHandCursor)
        self._resign_button.clicked.connect(self.resign_clicked.emit)
        layout.addWidget(self._resign_button)
        
        group.setLayout(layout)
        return group
    
    def _on_mode_changed(self, mode: str) -> None:
        """Handle game mode selection changes.
        
        Args:
            mode: The selected mode text.
        """
        is_pve = mode == "人机对战"
        
        # Enable/disable PVE-specific controls
        self._difficulty_label.setEnabled(is_pve)
        self._difficulty_combo.setEnabled(is_pve)
        self._color_label.setEnabled(is_pve)
        self._red_radio.setEnabled(is_pve)
        self._black_radio.setEnabled(is_pve)
        
        # Hint is only available in PVE mode
        self._hint_button.setEnabled(False)
    
    def get_settings(self) -> tuple:
        """Get the current game settings.
        
        Returns:
            A tuple of (mode, difficulty, player_color) where:
            - mode: "PVE" or "PVP"
            - difficulty: The difficulty level name
            - player_color: "RED" or "BLACK"
        """
        mode = "PVE" if self._mode_combo.currentText() == "人机对战" else "PVP"
        difficulty = self._difficulty_combo.currentText()
        player_color = "RED" if self._red_radio.isChecked() else "BLACK"
        
        return mode, difficulty, player_color
    
    def set_game_active(self, active: bool) -> None:
        """Set the game active state and update UI accordingly.
        
        Args:
            active: True if game is active, False otherwise.
        """
        # Disable settings during game
        self._mode_combo.setEnabled(not active)
        self._difficulty_combo.setEnabled(not active)
        self._red_radio.setEnabled(not active)
        self._black_radio.setEnabled(not active)
        
        # Update action buttons
        if active:
            self._start_button.setText("重新开始")
            self._undo_button.setEnabled(True)
            self._hint_button.setEnabled(True)
            self._resign_button.setEnabled(True)
        else:
            self._start_button.setText("开始游戏")
            self._undo_button.setEnabled(False)
            self._hint_button.setEnabled(False)
            self._resign_button.setEnabled(False)
    
    def add_notation(self, notation: str) -> None:
        """Add a move notation to the history list.
        
        Args:
            notation: The notation string to add.
        """
        move_number = self._notation_list.count() + 1
        text = f"{move_number}. {notation}"
        self._notation_list.addItem(text)
        self._notation_list.scrollToBottom()
    
    def clear_notation(self) -> None:
        """Clear all notation history."""
        self._notation_list.clear()
    
    def set_status(self, text: str, color: str = "blue") -> None:
        """Set the status label text and color.
        
        Args:
            text: The status message to display.
            color: Color name (blue, red, green, orange, black).
        """
        self._status_label.setText(text)
        self._status_label.setStyleSheet(StyleSheets.status_label(color))
    
    def show_thinking(self, show: bool) -> None:
        """Show or hide the thinking progress indicator.
        
        Args:
            show: True to show progress bar, False to hide.
        """
        self._progress_bar.setVisible(show)
        if show:
            self.set_status("AI思考中...", "orange")
            self._hint_button.setEnabled(False)
        else:
            self._hint_button.setEnabled(True)
    
    def enable_hint(self, enabled: bool) -> None:
        """Enable or disable the hint button.
        
        Args:
            enabled: True to enable, False to disable.
        """
        self._hint_button.setEnabled(enabled)
    
    @property
    def notation_list(self) -> QListWidget:
        """Get the notation list widget for external manipulation."""
        return self._notation_list
