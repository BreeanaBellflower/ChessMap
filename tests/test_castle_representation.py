import pytest
from src.chess_map_779 import ChessMap779
import chess
import numpy as np
import hashlib

@pytest.fixture
def converter():
    return ChessMap779()

def test_array_consistency(converter):
    fens = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
    ]

    for i, fen in enumerate(fens):
        board = chess.Board(fen)
        cmr = converter.board_to_cmr(board)
        cmr_board = converter.cmr_to_board(cmr)
        fen_board_array = converter.board_to_array(board)
        cmr_board_array = converter.board_to_array(cmr_board)
        assert np.array_equal(fen_board_array, cmr_board_array), f"Board mismatch at move {i}"

def test_cmr_to_fen_consistency(converter):
    fens = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
    ]

    for i, fen in enumerate(fens):
        board = chess.Board(fen)
        cmr = converter.board_to_cmr(board)
        cmr_board = converter.cmr_to_board(cmr)
        fen_board_array = converter.board_to_array(board)
        cmr_board_array = converter.board_to_array(cmr_board)
        # move numbers not preserved in castle representation, remove from fen
        assert np.array_equal(fen_board_array, cmr_board_array), f"Board mismatch at move {i}"
        assert board.fen().split()[:-3] == cmr_board.fen().split()[:-3], f"FEN mismatch at move {i}"

def test_en_passant(converter):
    fens = [
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
    ]

    for i, fen in enumerate(fens):
        board = chess.Board(fen)
        cmr = converter.board_to_cmr(board)
        cmr_board = converter.cmr_to_board(cmr)
        assert board.ep_square == cmr_board.ep_square, f"En passant square mismatch at move {i}"

def test_castling_rights(converter):
    fens = [
        "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
        "r3k2r/8/8/8/8/8/8/R3K2R b kq - 0 1",
        "r3k2r/8/8/8/8/8/8/R3K2R w KQ - 0 1",
        "r3k2r/8/8/8/8/8/8/R3K2R b k - 0 1",
    ]

    for i, fen in enumerate(fens):
        board = chess.Board(fen)
        cmr = converter.board_to_cmr(board)
        cmr_board = converter.cmr_to_board(cmr)
        assert board.castling_rights == cmr_board.castling_rights, f"Castling rights mismatch at move {i}"

def test_extract_metadata(converter):
    game = type('Game', (object,), {'headers': {'Event': 'Test Event', 'Site': 'Test Site'}})()
    metadata = converter.extract_metadata(game)
    assert metadata == {'Event': 'Test Event', 'Site': 'Test Site'}

def test_generate_game_id(converter):
    metadata = {
        'Event': 'Test Event',
        'Site': 'Test Site',
        'Date': '2023.10.01',
        'Round': '1',
        'White': 'Player1',
        'Black': 'Player2'
    }
    game_id = converter.generate_game_id(metadata)
    expected_id_string = 'Test Event_Test Site_2023.10.01_1_Player1_Player2'
    expected_game_id = hashlib.md5(expected_id_string.encode()).hexdigest()
    assert game_id == expected_game_id

def test_cmr_to_fen(converter):
    fens = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
    ]

    for fen in fens:
        board = chess.Board(fen)
        cmr = converter.board_to_cmr(board)
        fen_from_cmr = converter.cmr_to_fen(cmr)
        assert fen_from_cmr.split(' ')[:-3] == fen.split(' ')[:-3], f"FEN mismatch at move {i}"

def test_visualize_board(converter):
    fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    board = chess.Board(fen)
    cmr = converter.board_to_cmr(board)
    board_str = converter.visualize_board(cmr)
    print(board)
    expected_board_str = """r n b q k b n r
p p p p . p p p
. . . . . . . .
. . . . p . . .
. . . . P . . .
. . . . . . . .
P P P P . P P P
R N B Q K B N R"""
    assert board_str == expected_board_str
