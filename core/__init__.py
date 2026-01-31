"""Core game logic for Chinese Chess.

This package provides the core game logic including board state management,
rule validation, and notation generation.

Modules:
    board: Board state management and FEN parsing.
    constants: Game constants and helper functions.
    notation: Chinese notation generation.
    rules: Move validation and game state checking.
"""

from core.board import Board
from core.notation import NotationGenerator
from core.rules import RuleEngine

__all__ = ['Board', 'NotationGenerator', 'RuleEngine']
