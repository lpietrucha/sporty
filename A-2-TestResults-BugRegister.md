Executed by: Łukasz Pietrucha
Date Executed: 2026-11-17

Results:

SG-TS-1 - PASS
SG-TS-2 - FAIL, ISSUE-003, ISSUE-004, ISSUE-005, ISSUE-006
SG-TS-3 - FAIL, ISSUE-007
SG-TS-4 - FAIL, ISSUE-007
SG-TS-5 - PASS
SG-TS-6 - PASS
+additional exploration discovered other issues: ISSUE-001, ISSUE-002, ISSUE-008, ISSUE-009

Bug Register:
(resulting from scenarios executiong + exploratory testing)

#ISSUE-001: Match list displaying past events
Severity: High
Reproduction Steps:
1. Visit https://qae-assignment-tau.vercel.app/
2. Use valid user id within the address as a suffix: /?user-id=<valid-id-here>

Expected result:
1. The list should display Upcoming Football Matches

Actual result
1. The list contains also past events

Business Impact: 
1. Displaying past events might allow the user to place bets on non-existing events with known outcome

Evidence: https://drive.google.com/file/d/1jkg6InAbdxOk_dDEK6qTE2TKlBvvZpJk/view?usp=sharing 


#ISSUE-002: User can place bets on past events
Severity: Critical
Reproduction Steps:
1. Visit https://qae-assignment-tau.vercel.app/
2. Use valid user id within the address as a suffix: /?user-id=<valid-id-here>
3. Try to place bet on past event with valid stake (between 1 and 100 EUR)

Expected result:
1. User must not be allowed to place bets on past events

Actual result
1. User can place bet on past events

Business Impact: 
1. Allow the user to place bets on non-existing events with known outcome might result in financial loss

Evidence: 
1. https://drive.google.com/file/d/1ShieOCY8N3_Ne3O4el5Zvz-q1cATj5da/view?usp=sharing 
2. https://drive.google.com/file/d/1N8UwYSk3OZQUVOTUG_GeIVMTei3RUlTf/view?usp=sharing

#ISSUE-003: Missing information on receipt
Severity: High
Reproduction Steps:
1. Visit https://qae-assignment-tau.vercel.app/
2. Use valid user id within the address as a suffix: /?user-id=<valid-id-here>
3. Place bet on an upcoming event with valid stake (between 1 and 100 EUR)
4. Examin the receipt 

Expected result: 
1. The receipt should contain the following data: bet ID, match, selection, stake, odds, payout and timestamp

Actual result:
1. Selection is not displayed on the receipt

Business Impact: 
1. Company image might be affected as users will be confused about the summary of their bet 

Evidence:
https://drive.google.com/file/d/1KP07UboXRhlKkA6fWxXsMHhiuMP7BFDm/view?usp=sharing

#ISSUE-004: Wrong payout calculation on the receipt
Severity: Critical
Reproduction Steps:
1. Visit https://qae-assignment-tau.vercel.app/
2. Use valid user id within the address as a suffix: /?user-id=<valid-id-here>
3. Place bet on an upcoming event with valid stake (between 1 and 100 EUR), e.g. 10
4. Examin the receipt - check the payout  

Expected result: 
1. Payout should be calculated as as stake × odds. (This includes the original stake — so a €10 bet at 2.45 odds returns €24.50 total)
2. In the case of this executin odds was 1.85 and stake was 10, so payout should display 18.5 

Actual result:
1. Receipt shows wrong calculation, in this case 20

Business Impact: 
1. Wrong calculation of payouts will lead to financial loss 

Evidence: https://drive.google.com/file/d/14hPnkHvqc5VN5qkvY3FTj80ysaHwTdUK/view?usp=sharing

#ISSUE-005: Wrong match information on the receipt
Severity: High
Reproduction Steps:
1. Visit https://qae-assignment-tau.vercel.app/
2. Use valid user id within the address as a suffix: /?user-id=<valid-id-here>
3. Place bet on an upcoming event with valid stake (between 1 and 100 EUR)
4. Examin the receipt 

Expected result: 
1. According to domain context the match information should follow The "home" team is always listed first (left position), the "away" team second (right position). This convention carries through to the bet receipt

Actual result:
1. Home team is displayed as second, Away team is displayed as first on the receipt

Business Impact: 
1. Company image might be affected as users will be confused about the summary of their bet 

Evidence:
1. https://drive.google.com/file/d/1c02p11dBDUIsDbSlbkoV-AdIPnFK4xBN/view?usp=sharing
2. https://drive.google.com/file/d/1M95yqIyR7DyXZNq90IyTyN40JFlcsxCa/view?usp=sharing

#ISSUE-006: Stake is not deducted from the balance after placing a bet (UI)
Severity: High
Reproduction Steps:
1. Visit https://qae-assignment-tau.vercel.app/
2. Use valid user id within the address as a suffix: /?user-id=<valid-id-here>
3. Place bet on an upcoming event with valid stake (between 1 and 100 EUR)
4. Close the receipt 

Expected result: 
1. The balance drops by exactly the stake (e.g. €10.00)
2. Closing the receipt leaves no active selection

Actual result:
1. Balance stays intact on the screen (top-right corner)
2. Further investigation shows the following:
 a) if you refresh the screen, the balance gets updated 
 b) if you check the balance with API call /api/balance it was updated server-side

Business Impact: 
1. Company image might be affected as users will be confused about the summary of their bet 

Evidence: https://drive.google.com/file/d/1xDslrQbxYKSJJcYPEOOxHCm2JAhNmctX/view?usp=sharing


#ISSUE-007: User can reach negative balance
Severity: Critical
Reproduction Steps:
1. Visit https://qae-assignment-tau.vercel.app/
2. Use valid user id within the address as a suffix: /?user-id=<valid-id-here>
3. Place bet on an upcoming event with valid stake (between 1 and 100 EUR)
4. Close the receipt 
5. Keep betting with valid stakes several times, trying to exceed your original balance (e.g. place three bets 50 EUR each)

Expected result: 
1. Negative balance is not allowed

Actual result:
1. After placing a bet balance stays intact on the screen (top-right corner)
2. You can keep betting indefinitely if you don't refresh the page
3. Eventually the balance will be negative
4. Further investigation shows that there is no protection on API-level either - bet can be placed directly through API call (POST /api/place-bet) regardles of the balance for given user-id. 

Business Impact: 
1. The user must not be able to place a bet they cannot cover, the risk is financial loss.

Evidence: https://drive.google.com/file/d/1rm31VwxHHpQCJChLhV7GbbMfQK5xgxgd/view?usp=sharing

#ISSUE-008: Wrong currency in /api/place-bet response
Severity: Medium(?)/Low
Reproduction Steps:
1. Remember to use valid session token x-user-id in header
2. Send POST /api/place-bet with a valid matchId and selection
3. Examin the response

Expected result:
1. In response body all the details are displayed correctly, including the curreny

Actual result:
1. Curreny says "USD"

Business Impact: Consequences unknown for the moment - response is probably used somewhere for further processing so might result in "chain reaction"

Evidence: https://drive.google.com/file/d/1O2FE6EUqqof4PMyFq2NcjR4aq5vIzVp1/view?usp=sharing

#ISSUE-009: Balance discrepancies after calling /api/reset-balance
Severity: High
Reproduction Steps:
1. Remember to use valid session token x-user-id in header
2. Send POST /api/reset-balance
3. Send GET /api/balance
4. Examin the response

Expected result:
1. Balances displayed in response body of both calls should be the same in terms of amount and currency

Actual result:
1. In response body for reset-balance it says "balance": 125.5 and USD but if you get the balance right aftewards with a call from step 3 it shows "balance": 120, and EUR

Business Impact: To be examined further

Evidence: 
1. https://drive.google.com/file/d/1u0wZd4GfbefskAGA5gnR0QPjNYg6SWGz/view?usp=sharing
2. https://drive.google.com/file/d/1D8i6YmD04exf_EoYyd8JhDv9u1Gd-oJt/view?usp=sharing
