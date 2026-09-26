import pytest

from logic_utils import check_guess

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result, _ = check_guess(50, 50)
    assert result == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result, _ = check_guess(60, 50)
    assert result == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result, _ = check_guess(40, 50)
    assert result == "Too Low"

def test_winning_guess_message():
    # A correct guess should return the celebratory win message
    _, message = check_guess(50, 50)
    assert message == "🎉 Correct!"

def test_guess_too_high_message():
    # A guess above the secret should return the "go lower" message
    _, message = check_guess(60, 50)
    assert message == "📉 Go LOWER!"

def test_guess_too_low_message():
    # A guess below the secret should return the "go higher" message
    _, message = check_guess(40, 50)
    assert message == "📈 Go HIGHER!"

class TestCheckGuessTypeError:
    """check_guess's TypeError fallback assumes int(guess)/int(secret) can't fail.

    When the initial `guess > secret` comparison raises TypeError (mismatched
    types), the except block tries int(guess) and int(secret). If either value
    is something int() can't convert (e.g. None, a list, a dict), that call
    raises its own TypeError, which is never caught -- it escapes check_guess
    entirely instead of producing an error outcome.
    """

    def test_none_guess_raises_typeerror(self):
        with pytest.raises(TypeError):
            check_guess(None, 50)

    def test_none_secret_raises_typeerror(self):
        with pytest.raises(TypeError):
            check_guess(50, None)

    @pytest.mark.parametrize("guess", [[1, 2], {"a": 1}, object()])
    def test_uncastable_guess_type_raises_typeerror(self, guess):
        with pytest.raises(TypeError):
            check_guess(guess, 50)
