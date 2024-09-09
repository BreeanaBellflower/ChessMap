# ChessMap-779 Chess Board Representation

This project encodes a chess board state into a 779-dimensional vector.

Each square on the board is represented by a 12-dimensional one-hot encoded vector, where each dimension corresponds to a specific piece type and color. The mapping is as follows:

- Empty square: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- White pawn: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
- White knight: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
- White bishop: [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
- White rook: [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
- White queen: [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
- White king: [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
- Black pawn: [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
- Black knight: [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
- Black bishop: [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
- Black rook: [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- Black queen: [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
- Black king: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

Thus the full board of pieces, with 12 bits per square, is 64 * 12 = 768 bits.

Additional information is given by 11 additional values for turn, castling rights, and en passant square:

- Turn: 0 for white, 1 for black
- White kingside castling right: 1 if available, 0 otherwise
- White queenside castling right: 1 if available, 0 otherwise
- Black kingside castling right: 1 if available, 0 otherwise
- Black queenside castling right: 1 if available, 0 otherwise
- En passant square: 6-bit binary representation of the square index (0-63), or 000000 if not available

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/chess-converter.git
   cd chess-converter
   ```

2. Create and activate the Conda environment:
   ```
   make env
   conda activate chess-env
   ```

## Running Tests

After activating the environment, you can run the tests using:
   ```
   make test
   ```