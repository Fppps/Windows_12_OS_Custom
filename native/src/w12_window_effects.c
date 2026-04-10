#include "../include/w12_native.h"

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

int w12_native_desktop_blur_supported(void) {
#ifdef _WIN32
    return 1;
#else
    return 0;
#endif
}
