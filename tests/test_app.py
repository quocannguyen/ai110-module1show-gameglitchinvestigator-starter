import os

from streamlit.testing.v1 import AppTest

APP_PATH = os.path.join(os.path.dirname(__file__), "..", "app.py")


def make_app_in_cwd():
    """Build the AppTest without running it, so the caller can chdir
    (e.g. to isolate relative file I/O like high_score.txt) before
    the script actually executes."""
    return AppTest.from_file(APP_PATH)


def make_app():
    at = make_app_in_cwd()
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


def test_new_game_resets_status_from_lost_to_playing():
    # Regression for 30b5c7c: New Game must reset status back to "playing"
    # even when the previous game ended in "lost" (or "won"), otherwise the
    # status != "playing" guard keeps blocking play with the old game-over
    # message after starting a new game.
    at = make_app()
    at.sidebar.selectbox[0].set_value("Hard").run()  # attempt_limit = 5
    secret = at.session_state.secret
    wrong = opposite_guess(secret, 1, 50)

    for _ in range(5):
        at.text_input[0].set_value(str(wrong))
        at.button[0].click().run()

    assert at.session_state.status == "lost"

    at.button[1].click().run()  # "New Game" button

    assert at.session_state.status == "playing"
    assert not at.exception


def test_guess_input_and_submit_share_a_form():
    # Regression for the "Submit doesn't register on the first click" bug:
    # the guess text_input and its submit button must live in the same
    # st.form so the browser sends both in one atomic message instead of
    # racing the text_input's blur-triggered value sync against the
    # button's click-triggered rerun.
    at = make_app()

    guess_input = at.text_input[0]
    submit_button = next(b for b in at.button if b.proto.is_form_submitter)

    assert guess_input.proto.form_id != ""
    assert guess_input.proto.form_id == submit_button.proto.form_id


def test_attempts_left_banner_updates_on_the_submitting_run():
    # Regression: the "Attempts left" banner used to be rendered before
    # the submit handler incremented st.session_state.attempts, so it
    # lagged one guess behind until the next rerun. It must reflect the
    # decrement in the same run as the guess that caused it.
    at = make_app()
    secret = at.session_state.secret
    wrong = opposite_guess(secret, 1, 100)

    at.text_input[0].set_value(str(wrong))
    at.button[0].click().run()

    assert at.session_state.attempts == 1
    assert "Attempts left: 7" in at.info[0].value


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


def test_winning_creates_high_score_file_and_sets_session_state(tmp_path, monkeypatch):
    at = make_app_in_cwd()
    monkeypatch.chdir(tmp_path)
    at.run()
    secret = at.session_state.secret

    at.text_input[0].set_value(str(secret))
    at.button[0].click().run()

    assert at.session_state.status == "won"
    assert at.session_state.high_score == at.session_state.score
    assert (tmp_path / "high_score.txt").exists()
    assert int((tmp_path / "high_score.txt").read_text()) == at.session_state.score


def test_lower_score_win_does_not_lower_existing_high_score(tmp_path, monkeypatch):
    at = make_app_in_cwd()
    monkeypatch.chdir(tmp_path)
    (tmp_path / "high_score.txt").write_text("99999")

    at.run()
    secret = at.session_state.secret
    at.text_input[0].set_value(str(secret))
    at.button[0].click().run()

    assert at.session_state.status == "won"
    assert at.session_state.high_score == 99999
    assert int((tmp_path / "high_score.txt").read_text()) == 99999


def test_high_score_survives_new_game_reset(tmp_path, monkeypatch):
    at = make_app_in_cwd()
    monkeypatch.chdir(tmp_path)
    (tmp_path / "high_score.txt").write_text("42")

    at.run()
    at.button[1].click().run()  # "New Game" button

    assert at.session_state.high_score == 42


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
