# Single Bet Placement – test automation

Automated UI and API tests for the Single Bet Placement feature, built with
pytest, Selenium and requests.

## What is covered

| Test file | Scenario | Layer | Related issues |
| :--- | :--- | :--- | :--- |
| `tests/test_bet_placement.py` | SG-TS-2 Successful single bet placement | UI (Selenium), cross-checked with the API | ISSUE-003, 004, 005, 006 |
| `tests/test_place_bet_api.py` | SG-TS-4 Negative balance protection | API (requests) | ISSUE-007 |

The scenario IDs (SG-TS-*) refer to the test plan. The issue IDs refer to the
bug register. Failure messages name the related issue, so a red run points
straight to the bug.

## What you need locally

| Requirement | Why | Check |
| :--- | :--- | :--- |
| Python 3.12 or newer | Runs the tests | `python3 --version` |
| Google Chrome (current version) | Runs the UI test | Open Chrome, go to About Chrome |
| Git | Clones the repository | `git --version` |
| Internet access | Reaches the app under test. On the first UI run, Selenium Manager also downloads the matching ChromeDriver | – |
| A valid `x-user-id` | The API rejects unknown ids with `invalid_user_id` | Ask the team lead |

You do **not** need to install ChromeDriver yourself. Selenium Manager
(bundled with Selenium) downloads and caches it automatically.

## Setup (one time)

All commands run from the project root (the folder with this README).

1. Create and activate a virtual environment. `.venv/` is git-ignored.

   ```bash
   python3 -m venv .venv
   ```

   ```bash
   source .venv/bin/activate
   ```

   On Windows, activate with `.venv\Scripts\activate` instead.

2. Install the pinned dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Create your local `.env` file from the template.

   ```bash
   cp .env.example .env
   ```

   Open `.env` and set `SG_USER_ID` to your user id. `.env` is git-ignored, so
   your id stays on your machine. Never put it in `configs/`, `data/` or test
   code, and never commit it.

## Running the tests

Each time you open a new terminal, activate the virtual environment and load
your `.env` file:

```bash
source .venv/bin/activate
```

```bash
set -a; source .env; set +a
```

The second command exports every variable in `.env` to the current shell.
pytest does not read `.env` by itself.

Then run all tests:

```bash
pytest
```

Useful variations:

```bash
pytest tests/test_place_bet_api.py
```

```bash
SG_HEADLESS=false pytest tests/test_bet_placement.py
```

If `SG_USER_ID` is missing, every test errors out with
`Set the SG_USER_ID environment variable to a valid x-user-id.` Load your
`.env` file again and rerun.

### Environment variables

Set these in your `.env` file (see `.env.example`), or export them in the
shell for a single run.

| Variable | Required | Default | Purpose |
| :--- | :--- | :--- | :--- |
| `SG_USER_ID` | yes | – | Sent as the `x-user-id` header and the `?user-id=` URL parameter |
| `SG_BASE_URL` | no | value in `configs/config.json` | Run against another environment |
| `SG_HEADLESS` | no | `true` | Set to `false` to watch the browser |

Timeouts and the default base URL live in `configs/config.json`.

### Results

- pytest prints a summary of every failed check in the terminal.
- When a UI test fails, a browser screenshot is saved to `reports/`.

## Project layout

```
configs/      Environment settings (base URL, timeouts, headless)
data/         Test data, loaded into tests with @pytest.mark.parametrize
pages/        Page objects (BasePage with shared waits, BettingPage)
tests/        Test cases, one file per feature
utils/        API client, driver factory, config and data loaders, models
reports/      Failure screenshots (generated, not committed)
conftest.py   Shared fixtures and the failure screenshot hook
.env.example  Template for your local .env (the real .env is git-ignored)
.gitignore    Keeps secrets, virtual environments, caches and reports out of git
```

## How the tests work

- **Screen vs server.** The UI test compares what the page shows with
  `GET /api/balance`, before and after the bet.
- **Upcoming matches only.** Matches come from `GET /api/matches`, filtered to
  a future `kickoffDate`, because the list can also contain past events
  (ISSUE-001).
- **Soft assertions.** Receipt and balance checks use `pytest-check`, so one
  failing field does not hide the others.
- **Deterministic setup.** Every test resets the balance first and reads the
  real value from `GET /api/balance`, not from the reset response
  (ISSUE-009). The API test then places one setup bet to land on 90.00 before
  betting 100.00.

## Rules for contributors

- **Page objects do not assert.** They perform actions and return data. All
  assertions belong in `tests/`.
- **No hard-coded data in tests.** URLs and timeouts go in `configs/`, inputs
  go in `data/`, and secrets go in environment variables.
- **Keep tests independent.** Each test sets up its own state through
  fixtures and must pass when run alone.
- **Do not run tests in parallel.** All tests share one user id and reset its
  balance, so parallel runs (for example with `pytest-xdist`) would interfere
  with each other.
- **Naming.** Test files are `test_<feature>.py`, test functions are
  `test_<scenario>_<expected_outcome>`, and page files are `<name>_page.py` with
  a matching `PascalCase` class.
- **Style.** Follow `python-coding-rules.md`. Ruff settings are in
  `pyproject.toml`.

### Adding a test case

1. Add a new entry with a unique `id` to the relevant list in
   `data/bets.json`. The existing test picks it up automatically.
2. For a new scenario, add a `test_*` function in the matching file in
   `tests/`. If it needs new page elements, add locators and methods to the
   page object, not to the test.
