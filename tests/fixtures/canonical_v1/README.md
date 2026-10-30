# Explicitly synthetic canonical v1 fixtures

Created for this project's backend tests. These are not real restaurant records, Toast exports, Square exports, customer data or recorded AI output. No person/contact/payment-card fields are present.

- `valid.csv`: one order, two distinct lines for the same item; quantity 2 on each line. Each line has gross $20 and discount $2; second line has a cumulative $5 refund. Expected totals: 2 lines, 1 order, quantity 4 each, fulfilled 4 each, gross 4000 cents, discounts 400, refunds 500, net 3100. Refund does not undo fulfilled quantities.
- `invalid_duplicate.csv`: repeats the same line identity; whole import must fail.
- `invalid_values.csv`: negative quantity and excessive refund; whole import must fail.
- `malformed.csv`: wrong headers and incomplete quoting; whole import must fail.

More currency, timestamp/DST, update and atomicity fixtures are constructed explicitly in `tests/test_imports.py`. Date/time uses Los Angeles solely as a declared test configuration. It is not the timezone of the original pizza dataset and makes no claim about actual restaurant activity.
