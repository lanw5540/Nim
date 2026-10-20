import pytest

from nim import transition
def test_valid_action():
    assert transition((1, 3, 5), (1, 2)) == (1, 1, 5)

def test_take_whole_heap():
    assert transition((1, 3, 5), (2, 5)) == (1, 3, 0)

def test_take_single_object():
    assert transition((1,), (0, 1)) == (0,)

def test_original_board_unchanged():
    board = (1, 3, 5)
    transition(board, (0, 1))
    assert board == (1, 3, 5)

def test_returns_tuple():
    assert isinstance(transition((2, 2), (0, 1)), tuple)

def test_heap_too_large():
    with pytest.raises(IndexError):
        transition((1, 2), (2, 1))

def test_heap_negative():
    with pytest.raises(IndexError):
        transition((1, 2), (-1, 1))

def test_empty_board():
    with pytest.raises(IndexError):
        transition((), (0, 1))

def test_count_zero():
    with pytest.raises(ValueError):
        transition((1, 2), (0, 0))

def test_count_negative():
    with pytest.raises(ValueError):
        transition((1, 2), (1, -1))

def test_count_too_large():
    with pytest.raises(ValueError):
        transition((1, 2), (1, 3))

def test_empty_heap():
    with pytest.raises(ValueError):
        transition((0, 2), (0, 1))
