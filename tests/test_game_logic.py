import pytest

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    load_high_score,
    parse_guess,
    save_high_score,
)

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


class TestParseGuessDecimalTruncation:
    """parse_guess does int(float(raw)) for any string containing '.', which
    truncates toward zero instead of rounding -- "2.9" silently becomes 2.
    """

    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("1.9", 1),
            ("2.9", 2),
            ("-0.5", 0),
            ("-1.9", -1),
        ],
    )
    def test_decimal_strings_truncate_instead_of_round(self, raw, expected):
        ok, guess_int, err = parse_guess(raw)
        assert ok is True
        assert err is None
        assert guess_int == expected


class TestParseGuessWhitespaceAndSigns:
    """int() tolerates surrounding whitespace and a leading '+', so these
    should parse cleanly rather than being rejected as invalid input.
    """

    @pytest.mark.parametrize(
        "raw, expected",
        [
            (" 5 ", 5),
            ("+5", 5),
            ("05", 5),
            ("-5", -5),
        ],
    )
    def test_whitespace_and_sign_variants_parse_successfully(self, raw, expected):
        ok, guess_int, err = parse_guess(raw)
        assert ok is True
        assert err is None
        assert guess_int == expected


class TestParseGuessMalformedNumbers:
    """Thousands separators and scientific notation should be rejected with
    the friendly error message rather than raising an uncaught exception.
    """

    @pytest.mark.parametrize("raw", ["1,000", "1e2", "--5", "5-", "inf", "nan"])
    def test_malformed_numeric_strings_are_rejected_gracefully(self, raw):
        ok, guess_int, err = parse_guess(raw)
        assert ok is False
        assert guess_int is None
        assert err == "That is not a number."

    @pytest.mark.parametrize("raw", ["abc", "!!!", "五", None, ""])
    def test_non_numeric_input_is_rejected_gracefully(self, raw):
        ok, guess_int, err = parse_guess(raw)
        assert ok is False
        assert guess_int is None
        assert err is not None


class TestParseGuessOutOfDifficultyRange:
    """parse_guess never validates the parsed value against the active
    difficulty's (low, high) range, so wildly out-of-range guesses are
    accepted as 'ok' and silently compared via check_guess instead of
    surfacing a helpful validation error.
    """

    @pytest.mark.parametrize("difficulty", ["Easy", "Normal", "Hard"])
    def test_guess_far_above_range_is_still_parsed_as_ok(self, difficulty):
        _, high = get_range_for_difficulty(difficulty)
        ok, guess_int, err = parse_guess(str(high + 999999))
        assert ok is True
        assert err is None
        assert guess_int == high + 999999

    @pytest.mark.parametrize("difficulty", ["Easy", "Normal", "Hard"])
    def test_guess_far_below_range_is_still_parsed_as_ok(self, difficulty):
        low, _ = get_range_for_difficulty(difficulty)
        ok, guess_int, err = parse_guess(str(low - 999999))
        assert ok is True
        assert err is None
        assert guess_int == low - 999999

    def test_out_of_range_guess_still_resolves_to_a_hint_not_an_error(self):
        # Documents current behavior: an out-of-range guess gets "Too High"/
        # "Too Low" like any other wrong guess, with no range-aware message.
        outcome, _ = check_guess(999999, 50)
        assert outcome == "Too High"


class TestHighScorePersistence:
    def test_load_high_score_returns_zero_when_file_missing(self, tmp_path):
        path = tmp_path / "high_score.txt"
        assert load_high_score(str(path)) == 0

    def test_load_high_score_returns_zero_when_file_invalid(self, tmp_path):
        path = tmp_path / "high_score.txt"
        path.write_text("not a number")
        assert load_high_score(str(path)) == 0

    def test_save_then_load_round_trips_value(self, tmp_path):
        path = tmp_path / "high_score.txt"
        save_high_score(150, str(path))
        assert load_high_score(str(path)) == 150

    def test_save_high_score_overwrites_previous_value(self, tmp_path):
        path = tmp_path / "high_score.txt"
        save_high_score(100, str(path))
        save_high_score(200, str(path))
        assert load_high_score(str(path)) == 200
