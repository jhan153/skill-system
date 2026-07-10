#include "app.hpp"

int update(AppState& state, int delta) {
    state.value += delta;
    return state.value;
}

int main() {
    AppState state;
    return update(state, 1) == 1 ? 0 : 1;
}
