# Checkout parity fixture

`legacy-qt/` is the current checkout implementation and `candidate-dotnet/` is its replacement. Both are intended to implement the `create order` and `cancel order` capabilities against the fixtures in `fixtures/`.

Captured executions are under `artifacts/runtime/`. No captured execution exists for the cancel-order scenario. Treat the repository as an approved, self-contained analysis target; do not use network access or modify source files.
