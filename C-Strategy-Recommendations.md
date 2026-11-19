## 1. Why these 2 tests were selected for automation
I selected SG-TS-2 (successful bet placement through UI) and SG-TS-4 (negative balance protection on API level).

1. Both cover the basic, critical scenario of the app: placing a bet. Together they protect the user experience (what the user sees on the screen and on the receipt) and the business rules (what the server actually accepts and records)
2. They complement each other across layers. The UI test checks the screen against the server state (GET /api/balance), the API test checks that the server enforces the rules on its own, because UI validation can always be bypassed
3. They bring immediate value: both are currently failing and together they cover 5 of the 9 reported issues (ISSUE-003, 004, 005, 006 in SG-TS-2 and ISSUE-007 in SG-TS-4)
4. They can be made deterministic: the balance is reset before each test, and match data and odds are static for the session

Important note: 
1. possibly SG-TS-3 has the same root cause as SG-TS-4 (no balance check on the server), so automating it at the API level is faster and more stable

## 2. What was intentionally left as manual only

1. Exploratory testing. Areas where the behaviour is unclear and several bugs are found at once are better explored by a person. 4 of the 9 issues (ISSUE-001, 002, 008, 009) were found this way, outside the planned scenarios
2. Detailed receipt examination:
	2.1 The receipt currently has several defects, and part of its content (bet ID, timestamp) has no source in the API response. 
	2.2 Automating it requires a choice between soft checks and strict assertions, which makes sense only once the expected content is confirmed. 
	2.3 Until then, the automated test checks the key values (stake, odds, payout) and the full review stays manual
3. Error modal and retry (Rebet). There is no documented way to trigger a failed placement, so automating it would need request mocking, which adds complexity without a stable result
4. Filters, layout and usability. Lower risk, and the UI is likely to change, so automation would need frequent maintenance

## 3. Recommendations if the project were to scale

1. CI/CD and test layers.
   - Run API tests on every pull request: they are fast and catch the most critical (financial) defects
   - Run a small UI smoke suite against each deployment and the full suite nightly
   - Add contract tests that validate every response against the OpenAPI schema. This would have caught the wrong currency (ISSUE-008) and the reset-balance mismatch (ISSUE-009) automatically
   - Keep screenshots and HTML reports for every failed run

2. Test data strategy.
   - Use a dedicated test user ID for each parallel worker, so tests don't affect each other's balance or hit the 409 "bet in progress" rule
   - Provide a reliable way to set up and clean up data. reset-balance can't be trusted today (ISSUE-009) so tests read the balance with GET /api/balance instead
   - Add a test-only switch to force a failed placement, so the error modal and retry can be automated

3. Spec clarifications.
   - Status code for insufficient balance (not documented).
   - What makes a user ID valid. The header is the only credential, so anyone who knows another user's ID can act as that user
   - Source of the bet ID and placement timestamp on the receipt (not in the API response)
   - What counts as "upcoming": kickoffDate has no time, so same-day matches are ambiguous
   - Rounding rules for payout