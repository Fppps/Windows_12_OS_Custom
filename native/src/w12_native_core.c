#include "../include/w12_native.h"

static int restart_requested = 0;

const char *w12_native_version(void) {
    return "w12native-1U00";
}

int w12_native_restart_requested(void) {
    return restart_requested;
}

void w12_native_mark_restart(void) {
    restart_requested = 1;
}

int w12_native_clear_restart(void) {
    int previous = restart_requested;
    restart_requested = 0;
    return previous;
}
