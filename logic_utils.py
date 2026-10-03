def get_range_for_difficulty(difficulty: str):
    """
    Return the inclusive numeric guessing range for a given difficulty level.

    Args:
        difficulty: The difficulty name. Expected values are "Easy",
            "Normal", or "Hard". Any other value (including unrecognized
            strings) falls back to the "Normal" range.

    Returns:
        tuple[int, int]: A (low, high) pair representing the inclusive
        bounds of the range the secret number may fall within.

    Examples:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
        >>> get_range_for_difficulty("Unknown")
        (1, 100)
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str):
    """
    Parse raw user input into a validated integer guess.

    Accepts plain integer strings (e.g. "42") as well as decimal strings
    (e.g. "42.9"), which are truncated toward zero via float-to-int
    conversion. Empty input or None is treated as a missing guess rather
    than an invalid number.

    Args:
        raw: The raw string entered by the user, or None.

    Returns:
        tuple[bool, int | None, str | None]: A 3-tuple of
        (ok, guess_int, error_message):
            - ok: True if parsing succeeded, False otherwise.
            - guess_int: The parsed integer guess, or None on failure.
            - error_message: A human-readable error describing why
              parsing failed, or None on success.

    Examples:
        >>> parse_guess("42")
        (True, 42, None)
        >>> parse_guess("")
        (False, None, 'Enter a guess.')
        >>> parse_guess("abc")
        (False, None, 'That is not a number.')
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare a player's guess against the secret number.

    Args:
        guess: The player's guessed integer value.
        secret: The target integer value to guess.

    Returns:
        tuple[str, str]: A (outcome, message) pair where outcome is one
        of "Win", "Too High", or "Too Low", and message is a
        user-facing string describing the result.

    Examples:
        >>> check_guess(5, 5)
        ('Win', '🎉 Correct!')
        >>> check_guess(10, 5)
        ('Too High', '📉 Go LOWER!')
        >>> check_guess(1, 5)
        ('Too Low', '📈 Go HIGHER!')
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def load_high_score(path: str = "high_score.txt") -> int:
    """
    Read the persisted high score from disk.

    Args:
        path: Filesystem path to the high score file. Defaults to
            "high_score.txt" in the current working directory.

    Returns:
        int: The stored high score, or 0 if the file is missing,
        unreadable, or does not contain a valid integer.
    """
    try:
        with open(path, "r") as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0


def save_high_score(score: int, path: str = "high_score.txt") -> None:
    """
    Persist the high score to disk, overwriting any existing value.

    Args:
        score: The high score value to write.
        path: Filesystem path to write the high score to. Defaults to
            "high_score.txt" in the current working directory.

    Returns:
        None

    Raises:
        OSError: If the file cannot be opened or written to.
    """
    with open(path, "w") as f:
        f.write(str(score))


def update_score(current_score: int, outcome: str, attempt_number: int):
    """
    Compute the updated score after a single guess attempt.

    Scoring rules:
        - "Win": awards (100 - 10 * (attempt_number + 1)) points, with a
          minimum award of 10 points, added to the current score.
        - "Too High": awards +5 points on even-numbered attempts and
          -5 points on odd-numbered attempts.
        - "Too Low": deducts 5 points.
        - Any other outcome: the score is returned unchanged.

    Args:
        current_score: The player's score before this attempt.
        outcome: The result of the attempt, as returned by
            check_guess (e.g. "Win", "Too High", "Too Low").
        attempt_number: The zero-based index of the current attempt,
            used to scale the win bonus and alternate the "Too High"
            penalty/reward.

    Returns:
        int: The player's updated score after applying the outcome.

    Examples:
        >>> update_score(0, "Win", 0)
        90
        >>> update_score(0, "Too Low", 0)
        -5
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
