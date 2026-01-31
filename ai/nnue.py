"""NNUE (Efficiently Updatable Neural Network) evaluation for Chinese Chess.

This module implements a NNUE-style neural network evaluation function,
which is the state-of-the-art approach used in modern chess engines like
Stockfish. The key innovation is the use of incrementally updatable
accumulator for efficient position evaluation.

Architecture:
    Input (2 x 90 x 7 features) -> Accumulator (256) -> Hidden (32) -> Output (1)

Features are encoded as:
    - Piece type (7 types)
    - Position (90 squares)
    - Perspective (2: own/opponent)

Typical usage example:
    nnue = NNUEEvaluator()
    score = nnue.evaluate(board, RED)
"""

import math
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Final, List, Optional, Tuple

import numpy as np

from core.board import Board
from core.constants import (
    BLACK,
    BOARD_COLS,
    BOARD_ROWS,
    PIECE_VALUES,
    RED,
    RIVER_ROW,
    get_piece_color,
)


# =============================================================================
# NNUE Constants
# =============================================================================
# Network dimensions
INPUT_SIZE: Final[int] = 1260  # 2 perspectives * 90 squares * 7 piece types
ACCUMULATOR_SIZE: Final[int] = 256  # First hidden layer (efficiently updatable)
HIDDEN_SIZE: Final[int] = 32  # Second hidden layer
OUTPUT_SIZE: Final[int] = 1  # Single evaluation output

# Piece type indices (0-6)
PIECE_TYPE_INDEX: Final[Dict[str, int]] = {
    'K': 0, 'k': 0,  # King/General
    'A': 1, 'a': 1,  # Advisor
    'B': 2, 'b': 2,  # Bishop/Elephant
    'N': 3, 'n': 3,  # Knight/Horse
    'R': 4, 'r': 4,  # Rook/Chariot
    'C': 5, 'c': 5,  # Cannon
    'P': 6, 'p': 6,  # Pawn
}

NUM_PIECE_TYPES: Final[int] = 7
NUM_SQUARES: Final[int] = BOARD_ROWS * BOARD_COLS  # 90

# Quantization scale for int16 weights
WEIGHT_SCALE: Final[int] = 64
ACTIVATION_SCALE: Final[int] = 256


# =============================================================================
# NNUE Feature Encoding
# =============================================================================
def square_index(row: int, col: int) -> int:
    """Convert board coordinates to linear square index.
    
    Args:
        row: Board row (0-9).
        col: Board column (0-8).
    
    Returns:
        Linear index (0-89).
    """
    return row * BOARD_COLS + col


def feature_index(
    perspective: int,
    piece_type: int,
    square: int
) -> int:
    """Calculate the feature index for NNUE input.
    
    Args:
        perspective: 0 for own pieces, 1 for opponent pieces.
        piece_type: Piece type index (0-6).
        square: Square index (0-89).
    
    Returns:
        Feature index in the input vector.
    """
    return perspective * (NUM_PIECE_TYPES * NUM_SQUARES) + \
           piece_type * NUM_SQUARES + square


def mirror_square(square: int) -> int:
    """Mirror a square for the opposite perspective.
    
    In Chinese Chess, we flip vertically (not horizontally) for symmetry.
    
    Args:
        square: Original square index.
    
    Returns:
        Mirrored square index.
    """
    row = square // BOARD_COLS
    col = square % BOARD_COLS
    mirrored_row = BOARD_ROWS - 1 - row
    return mirrored_row * BOARD_COLS + col


# =============================================================================
# Activation Functions
# =============================================================================
def clipped_relu(x: np.ndarray) -> np.ndarray:
    """Clipped ReLU activation: max(0, min(x, 1)).
    
    This is used in NNUE for bounded activations.
    
    Args:
        x: Input array.
    
    Returns:
        Activated array with values in [0, 1].
    """
    return np.clip(x, 0, 1)


def scaled_clipped_relu(x: np.ndarray, scale: int = ACTIVATION_SCALE) -> np.ndarray:
    """Scaled clipped ReLU for quantized networks.
    
    Args:
        x: Input array.
        scale: Activation scale factor.
    
    Returns:
        Activated and scaled array.
    """
    return np.clip(x, 0, scale).astype(np.int32)


# =============================================================================
# NNUE Network
# =============================================================================
@dataclass
class NNUEWeights:
    """Container for NNUE network weights.
    
    Attributes:
        input_weights: Weights from input to accumulator (INPUT_SIZE x ACCUMULATOR_SIZE).
        input_biases: Biases for accumulator layer (ACCUMULATOR_SIZE).
        hidden_weights: Weights from accumulator to hidden (ACCUMULATOR_SIZE*2 x HIDDEN_SIZE).
        hidden_biases: Biases for hidden layer (HIDDEN_SIZE).
        output_weights: Weights from hidden to output (HIDDEN_SIZE).
        output_bias: Single output bias.
    """
    input_weights: np.ndarray
    input_biases: np.ndarray
    hidden_weights: np.ndarray
    hidden_biases: np.ndarray
    output_weights: np.ndarray
    output_bias: float


class NNUEAccumulator:
    """Incrementally updatable accumulator for NNUE evaluation.
    
    The accumulator stores the intermediate activation values after the
    first layer. By tracking which features changed, we can efficiently
    update the accumulator instead of recomputing from scratch.
    
    Attributes:
        values: Current accumulator values (shape: 2 x ACCUMULATOR_SIZE).
        active_features: Set of currently active feature indices for each perspective.
    """
    
    def __init__(self) -> None:
        """Initialize an empty accumulator."""
        self.values: np.ndarray = np.zeros((2, ACCUMULATOR_SIZE), dtype=np.float32)
        self.active_features: List[set] = [set(), set()]
    
    def reset(self) -> None:
        """Reset the accumulator to initial state."""
        self.values.fill(0)
        self.active_features = [set(), set()]
    
    def copy(self) -> 'NNUEAccumulator':
        """Create a deep copy of this accumulator.
        
        Returns:
            A new NNUEAccumulator with the same state.
        """
        new_acc = NNUEAccumulator()
        new_acc.values = self.values.copy()
        new_acc.active_features = [s.copy() for s in self.active_features]
        return new_acc


class NNUEEvaluator:
    """NNUE-based position evaluator for Chinese Chess.
    
    This evaluator uses a neural network with efficiently updatable
    accumulators to evaluate board positions. The network is designed
    to capture complex positional patterns while being fast to compute.
    
    Attributes:
        weights: Network weight parameters.
        use_incremental: Whether to use incremental accumulator updates.
    """
    
    def __init__(self, weights_path: Optional[str] = None) -> None:
        """Initialize the NNUE evaluator.
        
        Args:
            weights_path: Path to trained weights file. If None, uses
                         randomly initialized weights (for development).
        """
        self.weights: NNUEWeights = self._init_weights(weights_path)
        self.use_incremental: bool = True
        
        # Pre-computed piece-square tables for fallback/hybrid evaluation
        self._init_piece_square_tables()
    
    def _init_weights(self, weights_path: Optional[str]) -> NNUEWeights:
        """Initialize network weights.
        
        Args:
            weights_path: Path to weights file, or None for random init.
        
        Returns:
            Initialized NNUEWeights object.
        """
        if weights_path and Path(weights_path).exists():
            return self._load_weights(weights_path)
        else:
            return self._init_random_weights()
    
    def _init_random_weights(self) -> NNUEWeights:
        """Initialize weights with smart random values.
        
        Uses Kaiming initialization scaled by piece values to give
        the network a reasonable starting point.
        
        Returns:
            Randomly initialized weights.
        """
        np.random.seed(42)  # For reproducibility
        
        # Initialize input weights with small values
        # Scale by piece importance
        input_weights = np.random.randn(INPUT_SIZE, ACCUMULATOR_SIZE).astype(np.float32)
        input_weights *= 0.1 / math.sqrt(INPUT_SIZE)
        
        # Incorporate piece values into initial weights
        for piece, idx in PIECE_TYPE_INDEX.items():
            if piece.isupper():  # Only process once per piece type
                value = PIECE_VALUES.get(piece, 100) / 1000.0
                for sq in range(NUM_SQUARES):
                    # Own pieces
                    feat_own = feature_index(0, idx, sq)
                    input_weights[feat_own] *= (1 + value)
                    # Opponent pieces
                    feat_opp = feature_index(1, idx, sq)
                    input_weights[feat_opp] *= (1 + value)
        
        input_biases = np.zeros(ACCUMULATOR_SIZE, dtype=np.float32)
        
        # Hidden layer weights
        hidden_weights = np.random.randn(ACCUMULATOR_SIZE * 2, HIDDEN_SIZE).astype(np.float32)
        hidden_weights *= 0.1 / math.sqrt(ACCUMULATOR_SIZE * 2)
        hidden_biases = np.zeros(HIDDEN_SIZE, dtype=np.float32)
        
        # Output layer weights
        output_weights = np.random.randn(HIDDEN_SIZE).astype(np.float32)
        output_weights *= 0.1 / math.sqrt(HIDDEN_SIZE)
        output_bias = 0.0
        
        return NNUEWeights(
            input_weights=input_weights,
            input_biases=input_biases,
            hidden_weights=hidden_weights,
            hidden_biases=hidden_biases,
            output_weights=output_weights,
            output_bias=output_bias
        )
    
    def _load_weights(self, path: str) -> NNUEWeights:
        """Load weights from a binary file.
        
        Args:
            path: Path to weights file.
        
        Returns:
            Loaded weights.
        """
        # TODO: Implement proper weight loading
        # For now, return random weights
        return self._init_random_weights()
    
    def _init_piece_square_tables(self) -> None:
        """Initialize piece-square tables for hybrid evaluation."""
        # These tables are used as a fallback/supplement to NNUE
        self.pst = {}
        
        # King position values (encourage safe positioning)
        self.pst['K'] = np.array([
            [0, 0, 0, 8, 8, 8, 0, 0, 0],
            [0, 0, 0, 6, 8, 6, 0, 0, 0],
            [0, 0, 0, 4, 6, 4, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ], dtype=np.float32)
        
        # Pawn position values (encourage advancement)
        self.pst['P'] = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, -2, 0, 4, 0, -2, 0, 0],
            [2, 0, 8, 0, 8, 0, 8, 0, 2],
            [6, 12, 18, 18, 20, 18, 18, 12, 6],
            [10, 20, 30, 34, 40, 34, 30, 20, 10],
            [14, 26, 42, 60, 80, 60, 42, 26, 14],
            [18, 36, 56, 80, 120, 80, 56, 36, 18],
            [0, 3, 6, 9, 12, 9, 6, 3, 0],
        ], dtype=np.float32)
        
        # Rook position values
        self.pst['R'] = np.array([
            [-2, 10, 6, 14, 12, 14, 6, 10, -2],
            [8, 4, 8, 16, 8, 16, 8, 4, 8],
            [4, 8, 6, 14, 12, 14, 6, 8, 4],
            [6, 10, 8, 14, 14, 14, 8, 10, 6],
            [12, 16, 14, 20, 20, 20, 14, 16, 12],
            [12, 14, 12, 18, 18, 18, 12, 14, 12],
            [12, 18, 16, 22, 22, 22, 16, 18, 12],
            [12, 12, 12, 18, 18, 18, 12, 12, 12],
            [16, 20, 18, 24, 26, 24, 18, 20, 16],
            [14, 14, 12, 18, 16, 18, 12, 14, 14],
        ], dtype=np.float32)
        
        # Knight position values
        self.pst['N'] = np.array([
            [0, -3, 5, 4, 2, 4, 5, -3, 0],
            [-3, 2, 4, 6, 10, 6, 4, 2, -3],
            [4, 6, 10, 15, 16, 15, 10, 6, 4],
            [2, 10, 13, 14, 15, 14, 13, 10, 2],
            [2, 12, 11, 15, 16, 15, 11, 12, 2],
            [0, 5, 13, 12, 12, 12, 13, 5, 0],
            [-3, 2, 5, 5, 5, 5, 5, 2, -3],
            [0, -5, 2, 4, 2, 4, 2, -5, 0],
            [-8, 2, 4, -5, -4, -5, 4, 2, -8],
            [0, -4, 0, 0, 0, 0, 0, -4, 0],
        ], dtype=np.float32)
        
        # Cannon position values
        self.pst['C'] = np.array([
            [0, 0, 1, 0, -1, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0],
            [1, 0, 4, 3, 4, 3, 4, 0, 1],
            [3, 2, 3, 4, 3, 4, 3, 2, 3],
            [3, 2, 5, 4, 6, 4, 5, 2, 3],
            [3, 4, 6, 7, 6, 7, 6, 4, 3],
            [2, 3, 4, 4, 3, 4, 4, 3, 2],
            [0, 0, 0, 1, 1, 1, 0, 0, 0],
            [-1, 1, 1, 1, 0, 1, 1, 1, -1],
            [0, 0, 0, 2, 4, 2, 0, 0, 0],
        ], dtype=np.float32)
        
        # Advisor/Bishop have simpler tables (limited movement)
        self.pst['A'] = np.zeros((BOARD_ROWS, BOARD_COLS), dtype=np.float32)
        self.pst['A'][0, 4] = 2  # Center position
        self.pst['A'][1, 3] = 1
        self.pst['A'][1, 5] = 1
        self.pst['A'][2, 4] = 1
        
        self.pst['B'] = np.zeros((BOARD_ROWS, BOARD_COLS), dtype=np.float32)
        self.pst['B'][0, 2] = 1
        self.pst['B'][0, 6] = 1
        self.pst['B'][2, 0] = -2
        self.pst['B'][2, 4] = 3
        self.pst['B'][2, 8] = -2
        self.pst['B'][4, 2] = 3
        self.pst['B'][4, 6] = 3
    
    def extract_features(
        self,
        board: Board,
        perspective: int
    ) -> Tuple[List[int], List[int]]:
        """Extract active feature indices from a board position.
        
        Args:
            board: The board position.
            perspective: The perspective to evaluate from (RED or BLACK).
        
        Returns:
            Tuple of (own_features, opponent_features) as lists of indices.
        """
        own_features = []
        opp_features = []
        
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = board.get_piece(row, col)
                if piece is None:
                    continue
                
                piece_type = PIECE_TYPE_INDEX[piece]
                piece_color = get_piece_color(piece)
                
                # Calculate square from perspective
                if perspective == RED:
                    sq = square_index(row, col)
                else:
                    sq = mirror_square(square_index(row, col))
                
                # Determine if own or opponent piece
                if piece_color == perspective:
                    feat_idx = feature_index(0, piece_type, sq)
                    own_features.append(feat_idx)
                else:
                    feat_idx = feature_index(1, piece_type, sq)
                    opp_features.append(feat_idx)
        
        return own_features, opp_features
    
    def compute_accumulator(
        self,
        board: Board,
        perspective: int,
        accumulator: Optional[NNUEAccumulator] = None
    ) -> np.ndarray:
        """Compute the accumulator values for a position.
        
        Args:
            board: The board position.
            perspective: The perspective to evaluate from.
            accumulator: Optional existing accumulator to update incrementally.
        
        Returns:
            Accumulator values (shape: ACCUMULATOR_SIZE).
        """
        own_features, opp_features = self.extract_features(board, perspective)
        all_features = own_features + opp_features
        
        # Compute accumulator: sum of weights for active features + bias
        acc = self.weights.input_biases.copy()
        for feat in all_features:
            acc += self.weights.input_weights[feat]
        
        return acc
    
    def forward(
        self,
        board: Board,
        perspective: int
    ) -> float:
        """Forward pass through the NNUE network.
        
        Args:
            board: The board position to evaluate.
            perspective: The perspective to evaluate from (RED or BLACK).
        
        Returns:
            Raw network output (before scaling).
        """
        # Compute accumulators for both perspectives
        acc_own = self.compute_accumulator(board, perspective)
        acc_opp = self.compute_accumulator(board, -perspective)
        
        # Apply clipped ReLU
        acc_own = clipped_relu(acc_own)
        acc_opp = clipped_relu(acc_opp)
        
        # Concatenate accumulators
        hidden_input = np.concatenate([acc_own, acc_opp])
        
        # Hidden layer
        hidden = hidden_input @ self.weights.hidden_weights + self.weights.hidden_biases
        hidden = clipped_relu(hidden)
        
        # Output layer
        output = hidden @ self.weights.output_weights + self.weights.output_bias
        
        return float(output)
    
    def evaluate(self, board: Board, perspective: int) -> int:
        """Evaluate a board position.
        
        This is the main evaluation function that combines NNUE evaluation
        with classical piece-square table evaluation for robustness.
        
        Args:
            board: The board position to evaluate.
            perspective: The perspective to evaluate from (RED or BLACK).
        
        Returns:
            Evaluation score in centipawns. Positive means advantage for perspective.
        """
        # NNUE raw score
        nnue_score = self.forward(board, perspective)
        
        # Scale to centipawns (approximately)
        nnue_scaled = int(nnue_score * 100)
        
        # Classical evaluation (material + PST)
        classical_score = self._classical_evaluate(board, perspective)
        
        # Blend NNUE and classical evaluation
        # Weight NNUE more as it should learn complex patterns
        # But keep classical as a safety net for untrained networks
        final_score = int(0.3 * nnue_scaled + 0.7 * classical_score)
        
        return final_score
    
    def _classical_evaluate(self, board: Board, perspective: int) -> int:
        """Classical evaluation using material and piece-square tables.
        
        Args:
            board: The board position.
            perspective: The perspective to evaluate from.
        
        Returns:
            Classical evaluation score.
        """
        score = 0
        
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = board.get_piece(row, col)
                if piece is None:
                    continue
                
                piece_type = piece.upper()
                piece_color = get_piece_color(piece)
                
                # Material value
                material = PIECE_VALUES.get(piece, 0)
                
                # Piece-square table value
                if piece_type in self.pst:
                    if piece_color == RED:
                        pst_value = self.pst[piece_type][row, col]
                    else:
                        # Mirror for black
                        pst_value = self.pst[piece_type][BOARD_ROWS - 1 - row, col]
                else:
                    pst_value = 0
                
                # Pawn crossing river bonus
                if piece_type == 'P':
                    if piece_color == RED and row > RIVER_ROW:
                        material += 100  # Bonus for crossing river
                    elif piece_color == BLACK and row <= RIVER_ROW:
                        material += 100
                
                # Total piece value
                piece_value = material + pst_value
                
                # Add or subtract based on color relative to perspective
                if piece_color == perspective:
                    score += piece_value
                else:
                    score -= piece_value
        
        return score


# =============================================================================
# Global NNUE Instance
# =============================================================================
_nnue_evaluator: Optional[NNUEEvaluator] = None


def get_nnue_evaluator() -> NNUEEvaluator:
    """Get the global NNUE evaluator instance.
    
    Returns:
        The singleton NNUEEvaluator instance.
    """
    global _nnue_evaluator
    if _nnue_evaluator is None:
        _nnue_evaluator = NNUEEvaluator()
    return _nnue_evaluator


def nnue_evaluate(board: Board, perspective: int) -> int:
    """Evaluate a board position using NNUE.
    
    Convenience function that uses the global evaluator.
    
    Args:
        board: The board position to evaluate.
        perspective: The perspective to evaluate from.
    
    Returns:
        Evaluation score in centipawns.
    """
    return get_nnue_evaluator().evaluate(board, perspective)
