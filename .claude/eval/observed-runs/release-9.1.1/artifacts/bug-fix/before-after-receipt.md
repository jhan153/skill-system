# Before/after receipt

## Before

- Baseline commit: `c62438d`
- `README.md` SHA-256: `1b9f04c0383f7c551cb7975e438cbf522b977c45ea72429548d600cf8a249cb2`
- `src/fees.py` SHA-256: `107804166e3c7c4abbdd6e664dc68cd734ff098ab6289170fe698edd2e8cf690`
- `tests/test_fees.py` SHA-256: `00d7bf93cc64d37f789de8fc024f0a61400f61ac84895306aaed86851123794c`
- Command: `python3 -m unittest discover -s tests -v`
- Exit: `1`
- Signal: `AssertionError: 9650 != 10350`; one test failed.

## After

- `README.md` SHA-256: `1b9f04c0383f7c551cb7975e438cbf522b977c45ea72429548d600cf8a249cb2`
- `src/fees.py` SHA-256: `d72fa249a5b4ba59950865e8ae19d60ccaff33340f94118dfe53fc4f48ff680a`
- `tests/test_fees.py` SHA-256: `00d7bf93cc64d37f789de8fc024f0a61400f61ac84895306aaed86851123794c`
- Command: `python3 -m unittest discover -s tests -v`
- Exit: `0`
- Signal: one test passed; `OK`.
- Independent post-run check at `2026-07-10T18:44:25Z`: exit `0`, one test passed, `OK`.
- `git diff --check`: exit `0`.
- Worktree diff: only `src/fees.py`, changing the fee operation from subtraction to addition.

Result: the original failure was reproduced and then cleared by one source-line fix using the identical test command.
