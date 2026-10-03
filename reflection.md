# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Guess a number, submit on every other attempt (1st, 3rd, 5th...) | `check_guess` always compares the guess against the same secret number type | On odd-numbered attempts `app.py` compared the guess against `str(secret)` instead of `int(secret)`, so the comparison silently fell through a `TypeError` path with inconsistent results — the secret effectively "changed type" every other guess | No crash/traceback surfaced in the UI; bug only visible by noticing the hint logic behaved inconsistently between guesses |
| Guess higher than the secret (e.g. secret=50, guess=70) | Game shows "Too High" with a "Go LOWER" hint | Game showed "Too High" but told the player "📈 Go HIGHER!" — the hint text was swapped with the opposite comparison branch in `check_guess` | None — purely a logic/UX bug, no error output |
| Load the app for the first time | Info banner reads "Guess a number between 1 and 100" (or the actual configured range) | Banner always hardcoded "between 1 and 100" even when `low`/`high` were set to a different difficulty range, so the displayed range didn't match the real valid range | None |
| Start a new game, submit guesses, then click "New Game 🔁" after losing | `status` resets to "playing" and `attempts` resets to 0 so the player can try again | `attempts` was initialized to 1 (off-by-one, so "Attempts left" was wrong from the very first guess) and clicking "New Game" after a loss didn't reset `status`, leaving the game stuck in a "lost" state | None — required a regression test (`test_new_game_resets_attempts_and_status`) to actually catch, since the naive version of the test passed by coincidence |
| Type a guess into the text input and press Enter instead of clicking "Submit Guess" | The guess is submitted together with the button in one atomic action | Before wrapping both widgets in `st.form`, the text input fired its own rerun on Enter/blur separate from the button's rerun, so submission timing was inconsistent | None — surfaced as flaky/duplicate reruns rather than an error |
| Submit a guess and look at the "Attempts left" banner in the same run | Banner reflects the attempt count *after* the just-submitted guess | Banner was rendered before the submit handler incremented `st.session_state.attempts`, so it always showed last run's count and lagged one guess behind until the next rerun | None |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
  - Claude
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
  - AI explained that text_input sends an update on blur or Enter, while button fires its own rerun.
  - AI suggested wrapping input and submit button in st.form.
  - I reran and verified that the behavior is correct and asked AI to write tests/test_app.py/test_guess_input_and_submit_share_a_form.
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
  - I ran the app and manually verified the bug was no longer there.
  - I ran pytest and confirmed everything passed.
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
  - The manual test or pyteest showed me that my code fixed the bug.
- Did AI help you design or understand any tests? How?
  - Yes, AI gives me the reasoning, the tests, and their documenation.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
  - Every single time you interact with the app, Streamlit re-runs your entire Python script.
  - Session state is where it saves the memory.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
  - Use AI to explain the error or behavior.
  - Use AI to write test(s) for the error or behavior.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
