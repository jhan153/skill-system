# Kanboard integration fallback validation

Run the Skill System `integrations` verifier profile in an environment where its pytest probe is unavailable. The required fallback is the stdlib command `python3 -m unittest discover -s tests -q` in `integrations/kanboard-plan-sync`; a historical or expiring SKIP is not acceptable. Report the executed test count and exit status.
