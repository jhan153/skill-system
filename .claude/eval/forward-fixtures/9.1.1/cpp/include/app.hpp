#pragma once

struct AppState {
    int value = 0;
};

int update(AppState& state, int delta);
