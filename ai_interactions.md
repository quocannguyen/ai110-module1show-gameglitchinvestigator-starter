# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**What did the agent do?**

<!-- List the steps the agent took (files edited, commands run, etc.) -->

**What did you have to verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

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
