from streamlit.testing.v1 import AppTest


def make_app():
    at = AppTest.from_file("app.py")
    at.run()
    return at


def opposite_guess(secret, low, high):
    """A guess guaranteed to differ from secret while staying in range."""
    return secret + 1 if secret < high else low


def test_attempts_start_at_zero_not_one():
    # Regression for 7b6072a: attempts must start at 0 so the full
    # attempt limit is available on the first guess.
    at = make_app()
    assert at.session_state.attempts == 0
    assert at.info[0].value == (
        "Guess a number between 1 and 100. Attempts left: 8"
    )


def test_info_message_uses_difficulty_range_not_hardcoded_1_100():
    # Regression for 20fc825: the range shown must track the selected
    # difficulty instead of always saying "between 1 and 100".
    at = make_app()

    at.sidebar.selectbox[0].set_value("Easy").run()
    assert "between 1 and 20" in at.info[0].value
    assert at.session_state.attempts == 0

    at.sidebar.selectbox[0].set_value("Hard").run()
    assert "between 1 and 50" in at.info[0].value


def test_new_game_resets_attempts_and_status():
    at = make_app()
    at.sidebar.selectbox[0].set_value("Easy").run()

    at.button[1].click().run()  # "New Game" button

    assert at.session_state.status == "playing"
    assert at.session_state.attempts == 0


class TestNewGameIgnoresDifficultyRange:
    """"New Game" still calls random.randint(1, 100) unconditionally instead
    of random.randint(low, high). Switching to Easy/Hard and starting a new
    game can draw a secret outside the range the UI just advertised (e.g. 62
    on Easy, whose info banner says "between 1 and 20"). This characterizes
    the bug as currently committed rather than asserting the fix.
    """

    def test_new_game_can_draw_secret_outside_easy_range(self):
        at = make_app()
        at.sidebar.selectbox[0].set_value("Easy").run()

        secrets = set()
        for _ in range(30):
            at.button[1].click().run()
            secrets.add(at.session_state.secret)

        assert any(s > 20 for s in secrets), (
            "expected New Game's hardcoded randint(1, 100) to eventually "
            "produce a secret outside Easy's advertised 1-20 range"
        )


def test_correct_guess_wins_on_both_odd_and_even_attempt_numbers():
    # Regression for 96e670d + fc408b2: secret used to flip between int
    # and str depending on attempts parity, which crashed check_guess's
    # comparisons on even attempts. A win must succeed cleanly either way.
    at = make_app()
    secret = at.session_state.secret

    wrong = opposite_guess(secret, 1, 100)
    at.text_input[0].set_value(str(wrong))
    at.button[0].click().run()
    assert at.session_state.attempts == 1
    assert not at.exception

    at.text_input[0].set_value(str(secret))
    at.button[0].click().run()  # attempts becomes 2 (even) here
    assert not at.exception
    assert at.session_state.attempts == 2
    assert at.session_state.status == "won"


def test_out_of_attempts_sets_status_lost():
    at = make_app()
    at.sidebar.selectbox[0].set_value("Hard").run()  # attempt_limit = 5
    secret = at.session_state.secret
    wrong = opposite_guess(secret, 1, 50)

    for _ in range(5):
        at.text_input[0].set_value(str(wrong))
        at.button[0].click().run()

    assert at.session_state.attempts == 5
    assert at.session_state.status == "lost"
    assert not at.exception
