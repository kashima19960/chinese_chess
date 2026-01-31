"""Style constants for Chinese Chess UI.

This module defines the color palette, fonts, and style sheets for the
Chinese Chess application. The design follows the Soft UI Evolution style
with a light color scheme optimized for Chinese traditional aesthetics.

Design Reference:
    - Style: Soft UI Evolution (improved contrast, modern aesthetics)
    - Colors: Light pastels with Chinese traditional touches
    - Typography: Noto Serif SC / Noto Sans SC for Chinese characters
"""

from typing import Final


# =============================================================================
# Color Palette
# =============================================================================
class Colors:
    """Color constants for the application.
    
    The color scheme uses a warm, traditional Chinese aesthetic with:
    - Warm whites and creams for backgrounds
    - Deep reds and warm browns for accents
    - Soft shadows for depth
    """
    
    # Primary colors
    PRIMARY: Final[str] = "#8B4513"  # Saddle brown - traditional wood color
    PRIMARY_LIGHT: Final[str] = "#A0522D"  # Sienna
    PRIMARY_DARK: Final[str] = "#654321"  # Dark brown
    
    # Background colors
    BACKGROUND: Final[str] = "#FAF8F5"  # Warm white
    BACKGROUND_SECONDARY: Final[str] = "#F5F0E8"  # Light cream
    SURFACE: Final[str] = "#FFFFFF"  # Pure white for cards
    
    # Text colors
    TEXT_PRIMARY: Final[str] = "#2C2416"  # Dark brown for primary text
    TEXT_SECONDARY: Final[str] = "#5C5040"  # Medium brown for secondary text
    TEXT_MUTED: Final[str] = "#8C7A60"  # Light brown for muted text
    
    # Chess piece colors
    RED_PIECE_BG: Final[str] = "#FFF5E6"  # Warm cream for red pieces
    RED_PIECE_TEXT: Final[str] = "#C41E3A"  # Cardinal red
    RED_PIECE_BORDER: Final[str] = "#8B4513"  # Saddle brown border
    
    BLACK_PIECE_BG: Final[str] = "#2C2416"  # Dark brown for black pieces
    BLACK_PIECE_TEXT: Final[str] = "#F5F0E8"  # Light cream text
    BLACK_PIECE_BORDER: Final[str] = "#1A1610"  # Very dark brown border
    
    # Board colors
    BOARD_BG: Final[str] = "#DEB887"  # Burly wood - classic board color
    BOARD_LINE: Final[str] = "#5C4033"  # Dark brown lines
    BOARD_GRID: Final[str] = "#8B7355"  # Medium brown for grid
    
    # State colors
    SELECTED: Final[str] = "#FFD700"  # Gold for selection
    LEGAL_MOVE: Final[str] = "#4CAF50"  # Green for legal moves
    CAPTURE_HINT: Final[str] = "#E57373"  # Light red for capture hints
    HINT_MARKER: Final[str] = "#2196F3"  # Blue for hints
    
    # Status colors
    SUCCESS: Final[str] = "#4CAF50"  # Green
    WARNING: Final[str] = "#FF9800"  # Orange
    ERROR: Final[str] = "#F44336"  # Red
    INFO: Final[str] = "#2196F3"  # Blue
    
    # UI element colors
    BORDER: Final[str] = "#D4C4A8"  # Warm gray border
    SHADOW: Final[str] = "rgba(44, 36, 22, 0.1)"  # Soft shadow
    HOVER: Final[str] = "#F0E6D8"  # Light hover state
    DISABLED: Final[str] = "#C0B8A8"  # Disabled state


# =============================================================================
# Fonts
# =============================================================================
class Fonts:
    """Font constants for the application.
    
    Uses system fonts with Chinese font fallbacks for best compatibility.
    """
    
    # Font families
    PRIMARY: Final[str] = "SimHei"  # Primary Chinese font
    SECONDARY: Final[str] = "SimSun"  # Secondary Chinese font (for notation)
    FALLBACK: Final[str] = "Microsoft YaHei"  # Fallback font
    
    # Font sizes (in points)
    SIZE_TITLE: Final[int] = 24
    SIZE_HEADING: Final[int] = 16
    SIZE_BODY: Final[int] = 12
    SIZE_SMALL: Final[int] = 10
    SIZE_CAPTION: Final[int] = 9


# =============================================================================
# Dimensions
# =============================================================================
class Dimensions:
    """Dimension constants for UI elements."""
    
    # Border radius
    RADIUS_SMALL: Final[int] = 4
    RADIUS_MEDIUM: Final[int] = 8
    RADIUS_LARGE: Final[int] = 12
    
    # Spacing
    SPACING_XS: Final[int] = 4
    SPACING_SM: Final[int] = 8
    SPACING_MD: Final[int] = 12
    SPACING_LG: Final[int] = 16
    SPACING_XL: Final[int] = 24
    
    # Shadows (CSS format)
    SHADOW_SM: Final[str] = "2px 2px 4px rgba(44, 36, 22, 0.08)"
    SHADOW_MD: Final[str] = "4px 4px 8px rgba(44, 36, 22, 0.1)"
    SHADOW_LG: Final[str] = "6px 6px 12px rgba(44, 36, 22, 0.12)"
    
    # Neumorphism shadows (for Soft UI)
    SHADOW_SOFT_OUTER: Final[str] = (
        "5px 5px 10px rgba(44, 36, 22, 0.15), "
        "-5px -5px 10px rgba(255, 255, 255, 0.8)"
    )
    SHADOW_SOFT_INNER: Final[str] = (
        "inset 2px 2px 4px rgba(44, 36, 22, 0.1), "
        "inset -2px -2px 4px rgba(255, 255, 255, 0.7)"
    )


# =============================================================================
# Style Sheets
# =============================================================================
class StyleSheets:
    """Pre-built style sheets for common widgets."""
    
    @staticmethod
    def main_window() -> str:
        """Style sheet for the main window."""
        return f"""
            QMainWindow {{
                background-color: {Colors.BACKGROUND};
            }}
        """
    
    @staticmethod
    def title_bar() -> str:
        """Style sheet for the custom title bar."""
        return f"""
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
                padding: 4px 8px;
                border-radius: {Dimensions.RADIUS_SMALL}px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.2);
            }}
            QPushButton#closeButton:hover {{
                background-color: rgba(244, 67, 54, 0.8);
            }}
        """
    
    @staticmethod
    def control_panel() -> str:
        """Style sheet for the control panel."""
        return f"""
            QWidget {{
                background-color: {Colors.BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {Colors.BORDER};
                border-radius: {Dimensions.RADIUS_MEDIUM}px;
                margin-top: 12px;
                padding-top: 8px;
                background-color: {Colors.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                color: {Colors.TEXT_PRIMARY};
            }}
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
            }}
            QComboBox {{
                border: 1px solid {Colors.BORDER};
                border-radius: {Dimensions.RADIUS_SMALL}px;
                padding: 6px 12px;
                background-color: {Colors.SURFACE};
                color: {Colors.TEXT_PRIMARY};
                min-height: 24px;
            }}
            QComboBox:hover {{
                border-color: {Colors.PRIMARY_LIGHT};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                selection-background-color: {Colors.HOVER};
                selection-color: {Colors.TEXT_PRIMARY};
            }}
            QRadioButton {{
                color: {Colors.TEXT_PRIMARY};
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
            }}
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: {Colors.SURFACE};
                border: none;
                border-radius: {Dimensions.RADIUS_MEDIUM}px;
                padding: 10px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: {Colors.PRIMARY_DARK};
            }}
            QPushButton:disabled {{
                background-color: {Colors.DISABLED};
                color: {Colors.TEXT_MUTED};
            }}
            QListWidget {{
                border: 1px solid {Colors.BORDER};
                border-radius: {Dimensions.RADIUS_SMALL}px;
                background-color: {Colors.SURFACE};
                color: {Colors.TEXT_PRIMARY};
            }}
            QListWidget::item {{
                padding: 4px 8px;
            }}
            QListWidget::item:selected {{
                background-color: {Colors.HOVER};
                color: {Colors.TEXT_PRIMARY};
            }}
            QProgressBar {{
                border: 1px solid {Colors.BORDER};
                border-radius: {Dimensions.RADIUS_SMALL}px;
                background-color: {Colors.BACKGROUND_SECONDARY};
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {Colors.PRIMARY};
                border-radius: {Dimensions.RADIUS_SMALL}px;
            }}
        """
    
    @staticmethod
    def status_label(color: str = "blue") -> str:
        """Style sheet for status labels with different colors.
        
        Args:
            color: Color name (blue, red, green, orange, black).
        
        Returns:
            CSS style string for the status label.
        """
        color_map = {
            "blue": Colors.INFO,
            "red": Colors.RED_PIECE_TEXT,
            "green": Colors.SUCCESS,
            "orange": Colors.WARNING,
            "black": Colors.TEXT_PRIMARY,
        }
        actual_color = color_map.get(color, Colors.INFO)
        return f"color: {actual_color}; font-weight: bold;"


# =============================================================================
# Module exports
# =============================================================================
__all__ = [
    "Colors",
    "Fonts",
    "Dimensions",
    "StyleSheets",
]
