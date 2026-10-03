# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

"Plan and implement a 'High Score' tracker that saves your best score to a file." I asked it to work in plan mode first (so it couldn't edit code until I approved an approach), then implement. When it proposed a plan without tests, I rejected the plan once with "Add tests" so it would revise before I approved.

**What did the agent do?**

1. Read `app.py` and `logic_utils.py` to understand existing session-state patterns and scoring logic.
2. Drafted a plan: add `load_high_score`/`save_high_score` to `logic_utils.py`, wire them into `app.py`'s session-state init and the win branch, persist to `high_score.txt`.
3. After I asked for tests, it checked the existing `tests/` folder, found `tests/test_game_logic.py` (plain pytest unit tests) and `tests/test_app.py` (`AppTest`-based Streamlit regression tests), and extended the plan to match those existing patterns instead of inventing a new test style.
4. Implemented the plan:
   - **`logic_utils.py`** — added `load_high_score(path)` (returns 0 on missing/invalid file) and `save_high_score(score, path)`.
   - **`app.py`** — imported the new functions, initialized `st.session_state.high_score` on startup, displayed it via `st.sidebar.metric`, and updated/persisted it on a win that beats the stored record.
   - **`tests/test_game_logic.py`** — added `TestHighScorePersistence` covering missing file, invalid contents, round-trip, and overwrite, using `tmp_path` for isolation.
   - **`tests/test_app.py`** — added three `AppTest` regression tests (file created on win, lower score doesn't overwrite a higher stored score, high score survives "New Game").
5. Ran `pytest` itself after each change and iterated until all tests passed (26/26).

**What did you have to verify or fix manually?**

- First implementation pass put `st.sidebar.metric("High Score", st.session_state.high_score)` *before* the `if "high_score" not in st.session_state:` init block, causing an `AttributeError` at runtime. The agent caught this itself via the test run (not something I had to point out) and reordered the lines.
- The new `AppTest` file-isolation tests initially failed with `FileNotFoundError` because `AppTest.from_file("app.py")` resolves the script path lazily at `.run()` time relative to the *current* working directory — so `monkeypatch.chdir(tmp_path)` before `.run()` broke the lookup of `app.py` itself. The agent fixed this by resolving `app.py` to an absolute path (`APP_PATH`) up front, decoupling "where to find the script" from "where the script's relative file I/O lands." It also initially left a redundant `make_app()`/`make_app_in_cwd()` pair with duplicated logic; when I asked "can we refactor `make_app` to use `make_app_in_cwd`?", it collapsed `make_app` into a one-line wrapper around `make_app_in_cwd()`, removing the duplication.
- I reviewed the diff myself (session-state ordering, where the persistence check lived relative to the win branch, and that the sidebar metric didn't disturb existing widget-index assumptions like `at.sidebar.selectbox[0]` in other tests) rather than accepting it blind — everything checked out, so no further manual code changes were needed beyond the two rounds of back-and-forth above.

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Decimal strings truncate instead of round | "identify three potential 'edge case' inputs that might still break the game." → "generate a suite of pytest cases that verify the game handles these inputs gracefully." | `TestParseGuessDecimalTruncation` in `tests/test_game_logic.py`: asserts `"2.9"` parses to `2`, `"-0.5"` parses to `0`, etc. | Yes | `parse_guess` does `int(float(raw))`, which truncates toward zero rather than rounding — a player typing `2.9` expecting it to round to `3` gets silently misparsed to `2`. |
| Whitespace/sign-prefixed numbers | Same prompts as above | `TestParseGuessWhitespaceAndSigns`: asserts `" 5 "`, `"+5"`, `"05"`, `"-5"` all parse successfully to their numeric value | Yes | `int()` natively tolerates these forms, so the test documents/locks in that normal-looking input isn't incorrectly rejected as invalid. |
| Malformed numeric strings (thousands separators, scientific notation, `inf`/`nan`) | Same prompts as above | `TestParseGuessMalformedNumbers`: asserts `"1,000"`, `"1e2"`, `"--5"`, `"inf"`, `"nan"`, etc. return `ok=False` with the friendly `"That is not a number."` message instead of raising | Yes | These look numeric to a user but aren't handled by `parse_guess`'s simple `int`/`float` logic, so the test guards against an uncaught exception crashing the app on input like this. |
| Guesses far outside the difficulty's valid range | Same prompts as above | `TestParseGuessOutOfDifficultyRange`: asserts a guess like `high + 999999` or `low - 999999` is still accepted as `ok=True` by `parse_guess`, and `check_guess` just returns "Too High"/"Too Low" | Yes (documents existing gap, not a crash) | `parse_guess` never checks the parsed value against `get_range_for_difficulty`'s `(low, high)`, so a wildly out-of-range guess wastes an attempt with no helpful validation message — this test exists to flag that known limitation rather than hide it. |

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
<!-- Paste the prompt you gave the AI -->
```

**Linting output before:**

```
<!-- Paste relevant linter warnings/errors -->
```

**Changes applied:**

<!-- Describe what you changed based on the AI's suggestions -->

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
