import numpy as np
import chess
import hashlib
import chess.pgn
import io

# additional cm779 bits are:
# 0: 0 if white to move, 1 if black to move
# 1: 1 if white has kingside castling rights, 0 otherwise
# 2: 1 if white has queenside castling rights, 0 otherwise
# 3: 1 if black has kingside castling rights, 0 otherwise
# 4: 1 if black has queenside castling rights, 0 otherwise
# 5-10: the bit representation of the en passant square
piece_to_binary = {
    '.': np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    'P': np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]),
    'N': np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]),
    'B': np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]),
    'R': np.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]),
    'Q': np.array([0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]),
    'K': np.array([0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]),
    'p': np.array([0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]),
    'n': np.array([0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]),
    'b': np.array([0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]),
    'r': np.array([0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    'q': np.array([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    'k': np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
}
binary_to_piece = {tuple(v): k for k, v in piece_to_binary.items()}

class ChessMap779:
    """
    ChessMap779 Utilities.

    12 x 64 bits for the board and which piece is on which square.
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
    def board_to_cm779(board):
        """
        Convert a chess board to a CM779 representation.
        """
        pieces_cm779 = np.zeros((64, 12), dtype=int)
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                pieces_cm779[square] = piece_to_binary[piece.symbol()]
            else:
                pieces_cm779[square] = piece_to_binary['.']

        additional_cm779 = np.zeros(11, dtype=int)
        additional_cm779[0] = 0 if board.turn == chess.WHITE else 1
        additional_cm779[1] = 1 if board.has_kingside_castling_rights(chess.WHITE) else 0
        additional_cm779[2] = 1 if board.has_queenside_castling_rights(chess.WHITE) else 0
        additional_cm779[3] = 1 if board.has_kingside_castling_rights(chess.BLACK) else 0
        additional_cm779[4] = 1 if board.has_queenside_castling_rights(chess.BLACK) else 0
        if board.ep_square is not None:
            ep_square_bin = format(board.ep_square, '06b')
            additional_cm779[5:11] = np.array(list(map(int, ep_square_bin)))

        return np.concatenate((pieces_cm779.flatten(), additional_cm779))

    @staticmethod
    def split_cm779(cm779):
        """
        Split a CM779 representation into pieces and additional data.
        """
        pieces_cm779 = cm779[:768].reshape((64, 12))
        additional_cm779 = cm779[768:]
        return pieces_cm779, additional_cm779

    @staticmethod
    def cm779_to_board(cm779):
        """
        Convert a CM779 representation to a chess board.
        """
        pieces_cm779, additional_cm779 = ChessMap779.split_cm779(cm779)
        board = chess.Board(None)
        for square in chess.SQUARES:
            piece_data = tuple(pieces_cm779[square])
            if piece_data != tuple(piece_to_binary['.']):
                piece_symbol = binary_to_piece[piece_data]
                board.set_piece_at(square, chess.Piece.from_symbol(piece_symbol))

        board.turn = chess.WHITE if additional_cm779[0] == 0 else chess.BLACK
        castling_rights = additional_cm779[1:5]
        board.clean_castling_rights()
        if castling_rights[0] == 1:
            board.castling_rights |= chess.BB_H1
        if castling_rights[1] == 1:
            board.castling_rights |= chess.BB_A1
        if castling_rights[2] == 1:
            board.castling_rights |= chess.BB_H8
        if castling_rights[3] == 1:
            board.castling_rights |= chess.BB_A8

        en_passant_square = int(''.join(map(str, additional_cm779[5:11])), 2)
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
    def cm779_to_fen(cm779):
        """
        Convert a CM779 representation to a FEN string.
        """
        board = ChessMap779.cm779_to_board(cm779)
        return board.fen()

    @staticmethod
    def visualize_board(cm779):
        """
        Visualize the board from a CM779 representation.
        """
        board = ChessMap779.cm779_to_board(cm779)
        return str(board)

    @staticmethod
    def pgn_to_cm779_file(pgn_directory, cm779_file_path):
        """
        Convert all PGN files in a directory to a CM779 file.
        """
        import os

        with open(cm779_file_path, 'w') as cm779_file:
            # Write CSV header
            cm779_file.write(','.join([f'cm779_{i}' for i in range(779)] + ['game_id', 'move_half_number']) + '\n')

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
                                game_id = ChessMap779.generate_game_id(ChessMap779.extract_metadata(game))

                                # Convert moves to CM779 representation
                                board = game.board()
                                move_half_number = 0

                                cm779 = ChessMap779.board_to_cm779(board)
                                cm779_file.write(','.join(map(str, cm779.tolist() + [game_id, move_half_number])) + '\n')

                                for move in game.mainline_moves():
                                    board.push(move)
                                    move_half_number += 1
                                    cm779 = ChessMap779.board_to_cm779(board)
                                    cm779_file.write(','.join(map(str, cm779.tolist() + [game_id, move_half_number])) + '\n')
                            except Exception as e:
                                print(f"Error processing game: {e}")
                                continue

if __name__ == "__main__":
    chessmap = ChessMap779()
    chessmap.pgn_to_cm779_file('data/pgn/', 'data/championships.csv')