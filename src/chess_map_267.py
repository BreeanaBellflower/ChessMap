import numpy as np
import chess
import hashlib
import chess.pgn
import io

# additional cm267 bits are:
# 0: 0 if white to move, 1 if black to move
# 1: 1 if white has kingside castling rights, 0 otherwise
# 2: 1 if white has queenside castling rights, 0 otherwise
# 3: 1 if black has kingside castling rights, 0 otherwise
# 4: 1 if black has queenside castling rights, 0 otherwise
# 5-10: the bit representation of the en passant square
piece_to_binary = {
    '.': np.array([0, 0, 0, 0]),
    'P': np.array([0, 0, 0, 1]),
    'N': np.array([0, 0, 1, 0]),
    'B': np.array([0, 0, 1, 1]),
    'R': np.array([0, 1, 0, 0]),
    'Q': np.array([0, 1, 0, 1]),
    'K': np.array([0, 1, 1, 0]),
    'p': np.array([1, 0, 0, 1]),
    'n': np.array([1, 0, 1, 0]),
    'b': np.array([1, 0, 1, 1]),
    'r': np.array([1, 1, 0, 0]),
    'q': np.array([1, 1, 0, 1]),
    'k': np.array([1, 1, 1, 0])
}
binary_to_piece = {tuple(v): k for k, v in piece_to_binary.items()}
# Fill in any missing combinations with '.'
for i in range(16):  # 2^4 = 16 possible combinations
    binary = tuple(np.array([int(b) for b in f'{i:04b}']))
    if binary not in binary_to_piece:
        binary_to_piece[binary] = '.'

piece_embedding_size = 4
board_binary_size = 64 * piece_embedding_size
additional_cm267_size = 11

class ChessMap267:
    """
    ChessMap267 Utilities.

    7 x 64 bits for the board and which piece is on which square.
    11 bits for additional information:
    0: 0 if white to move, 1 if black to move
    1: 1 if white has kingside castling rights, 0 otherwise
    2: 1 if white has queenside castling rights, 0 otherwise
    3: 1 if black has kingside castling rights, 0 otherwise
    4: 1 if black has queenside castling rights, 0 otherwise
    5-10: the bit representation of the en passant square
    """

    @staticmethod
    def extract_metadata(game):
        """
        Extract metadata from a PGN game.
        """
        return {key: value for key, value in game.headers.items()}

    @staticmethod
    def generate_game_id(metadata):
        """
        Generate a unique game ID based on available metadata.
        """
        id_components = [
            metadata.get('Event', ''),
            metadata.get('Site', ''),
            metadata.get('Date', ''),
            metadata.get('Round', ''),
            metadata.get('White', ''),
            metadata.get('Black', '')
        ]
        id_string = '_'.join(filter(None, id_components))
        return hashlib.md5(id_string.encode()).hexdigest()

    @staticmethod
    def board_to_cm267(board):
        """
        Convert a chess board to a CM267 representation.
        """
        pieces_cm267 = np.zeros((64, piece_embedding_size), dtype=int)
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                pieces_cm267[square] = piece_to_binary[piece.symbol()]
            else:
                pieces_cm267[square] = piece_to_binary['.']

        additional_cm267 = np.zeros(11, dtype=int)
        additional_cm267[0] = 0 if board.turn == chess.WHITE else 1
        additional_cm267[1] = 1 if board.has_kingside_castling_rights(chess.WHITE) else 0
        additional_cm267[2] = 1 if board.has_queenside_castling_rights(chess.WHITE) else 0
        additional_cm267[3] = 1 if board.has_kingside_castling_rights(chess.BLACK) else 0
        additional_cm267[4] = 1 if board.has_queenside_castling_rights(chess.BLACK) else 0
        if board.ep_square is not None:
            ep_square_bin = format(board.ep_square, '06b')
            additional_cm267[5:11] = np.array(list(map(int, ep_square_bin)))

        return np.concatenate((pieces_cm267.flatten(), additional_cm267))

    @staticmethod
    def split_cm267(cm267):
        """
        Split a CM267 representation into pieces and additional data.
        """
        pieces_cm267 = cm267[:board_binary_size].reshape((64, piece_embedding_size))
        additional_cm267 = cm267[board_binary_size:]
        return pieces_cm267, additional_cm267

    @staticmethod
    def cm267_to_board(cm267):
        """
        Convert a CM267 representation to a chess board.
        """
        pieces_cm267, additional_cm267 = ChessMap267.split_cm267(cm267)
        board = chess.Board(None)
        for square in chess.SQUARES:
            piece_data = tuple(pieces_cm267[square])
            if binary_to_piece[piece_data] != '.':
                piece_symbol = binary_to_piece[piece_data]
                board.set_piece_at(square, chess.Piece.from_symbol(piece_symbol))

        board.turn = chess.WHITE if additional_cm267[0] == 0 else chess.BLACK
        castling_rights = additional_cm267[1:5]
        board.clean_castling_rights()
        if castling_rights[0] == 1:
            board.castling_rights |= chess.BB_H1
        if castling_rights[1] == 1:
            board.castling_rights |= chess.BB_A1
        if castling_rights[2] == 1:
            board.castling_rights |= chess.BB_H8
        if castling_rights[3] == 1:
            board.castling_rights |= chess.BB_A8

        en_passant_square = int(''.join(map(str, additional_cm267[5:11])), 2)
        if en_passant_square < 64:
            board.ep_square = en_passant_square

        return board

    @staticmethod
    def board_to_array(board):
        """
        Convert a board to a 2D array.
        """
        array = []
        for rank in range(8):
            row = []
            for file in range(8):
                square = chess.square(file, 7 - rank)
                piece = board.piece_at(square)
                if piece is None:
                    row.append('.')
                else:
                    row.append(piece.symbol())
            array.append(row)
        return array

    @staticmethod
    def cm267_to_fen(cm267):
        """
        Convert a CM267 representation to a FEN string.
        """
        board = ChessMap267.cm267_to_board(cm267)
        return board.fen()

    @staticmethod
    def visualize_board(cm267):
        """
        Visualize the board from a CM267 representation.
        """
        board = ChessMap267.cm267_to_board(cm267)
        return str(board)

    @staticmethod
    def pgn_to_cm267_file(pgn_directory, cm267_file_path):
        """
        Convert all PGN files in a directory to a CM267 file.
        """
        import os

        with open(cm267_file_path, 'w') as cm267_file:
            # Write CSV header
            cm267_file.write(','.join([f'cm267_{i}' for i in range(267)] + ['game_id', 'move_half_number']) + '\n')

            for filename in os.listdir(pgn_directory):
                if filename.endswith('.pgn'):
                    pgn_file_path = os.path.join(pgn_directory, filename)
                    with open(pgn_file_path, 'r') as pgn_file:
                        while True:
                            try:
                                game = chess.pgn.read_game(pgn_file)
                                if game is None:
                                    break

                                # Generate game ID
                                game_id = ChessMap267.generate_game_id(ChessMap267.extract_metadata(game))

                                # Convert moves to CM267 representation
                                board = game.board()
                                move_half_number = 0

                                cm267 = ChessMap267.board_to_cm267(board)
                                cm267_file.write(','.join(map(str, cm267.tolist() + [game_id, move_half_number])) + '\n')

                                for move in game.mainline_moves():
                                    board.push(move)
                                    move_half_number += 1
                                    cm267 = ChessMap267.board_to_cm267(board)
                                    cm267_file.write(','.join(map(str, cm267.tolist() + [game_id, move_half_number])) + '\n')
                            except Exception as e:
                                print(f"Error processing game: {e}")
                                continue

if __name__ == "__main__":
    chessmap = ChessMap267()
    chessmap.pgn_to_cm267_file('data/pgn/', 'data/championships.csv')