#Sporty Group Take Home Exercise Part 1 - Test Plan

The most important principle I would follow for the entire task is: checking that the screen works and that what the user sees matches what was actually accepted and recorded "under the hood". 
That secures the basics and allows a proper balance between keeping the user happy and protecting the business.

# SG-TS-1 
Title: Unauthorized access attempt - all endpoints reject requests without x-user-id (API)
Priority: Critical
Risk rationale: The spec requires the header on every endpoint. One unprotected endpoint leaks data (balance, matches) or allows a state change (reset-balance).

Steps:
1. Send each request without the x-user-id header: GET /api/matches, GET /api/balance, POST /api/reset-balance, POST /api/place-bet.

Expected Result:
1. Every response is 401 with error missing_user_id.
2. No response contains match, balance or bet data.
3. reset-balance does not reset anything (verify with a valid user)


# SG-TS-2 
Title: Successful single bet placement 
Priority: Critical
Risk rationale: This is the core and only feature in scope. If it fails or deducts the wrong amount, the product is unusable/confusing.

Steps:
1. Reset the balance and note the available balance
2. Click an odds button (e.g. 1) on any upcoming match
3. Enter a valid stake, e.g. 10.00
4. Click Place Bet
5. Close the receipt modal

Expected Result:
1. The bet slip shows the selection, the stake and a payout equal to stake × odds
2. The button shows Placing..., then the receipt modal appears
3. The receipt shows bet ID, match, selection, stake, odds, payout and timestamp
4. The balance drops by exactly the stake (e.g. €10.00)
5. Closing the receipt leaves no active selection
 
# SG-TS-3
Title: Negative balance protection (UI)  
Priority: Critical 
Risk rationale: Accepting a bet the user cannot cover creates a negative balance and direct financial loss for the operator

Steps:
1. Place bets until the available balance is below certain number, e.g. 100.00
2. Click an odds button (e.g. 1) on any upcoming match
3. Enter a stake above the balance but within limits, e.g. 100.00
4. Click Place Bet

Expected Result:
1. UI shows "Insufficient balance" and no bet is placed
2. No bet is placed and no receipt appears.
3. Displayed balance is unchanged.

# SG-TS-4
# Title: Negative balance protection in POST /api/place-bet (API)
Priority: Critical 
Risk rationale: Accepting a bet the user cannot cover creates a negative balance and direct financial loss for the operator

Steps:
1. Place bets through the API until the balance is below 100.00, and read it with GET /api/balance
2. Send POST /api/place-bet with a valid matchId and selection, and stake 100.00
3. Read GET /api/balance again

Expected Result:
1. Request is rejected with error insufficient_balance (status code is not documented, 422 expected)
2. Balance is unchanged and never goes negative

# SG-TS-5
Title: Stake boundary validation (UI) 
Priority: High
Risk rationale: Stake limits are business rules protecting both the user and the operator

Steps:
1. Select an outcome so the bet slip is active.
2. Try to place a bet with each stake: empty, abc, 0.99, 1.00, 1.01, 100.00, 100.01, 10.555

Expected Result:
1. Empty: placement is blocked
2. abc: input is not accepted as a stake; placement is blocked
3. 0.99: rejected with "Minimum stake is €1.00"
4. 1.00: accepted 
5. 100.00: accepted
6. 100.01: rejected with "Maximum stake is €100.00"
7. 10.555: third decimal is not accepted or the stake is rejected for precision
8. Balance is unchanged after every rejected attempt

# SG-TS-6
Title: Stake boundary validation in POST /api/place-bet (API) 
Priority: High
Risk rationale: Stake limits are business rules protecting both the user and the operator

Steps:
1. Reset the balance and read it with GET /api/balance
2. Get a valid matchId from GET /api/matches
3. Send POST /api/place-bet with a valid matchId and selection, and each stake: missing, "abc", 0.99, 1.00, 100.00, 100.01, 10.555
4. After each rejected request read GET /api/balance

Expected Result:
1. Missing or "abc": 422 invalid_stake_type
2. 0.99: 422 invalid_stake_min
3. 1.00: 200 per business rules and OpenAPI (minimum: 1), with the stake reflected in the response and the balance reduced by the stake
4. 100.00: 200, with the stake reflected in the response and the balance reduced by the stake
5. 100.01: 422 invalid_stake_max
6. 10.555: 422 invalid_stake_precision
7. Balance is unchanged after every 422 response
