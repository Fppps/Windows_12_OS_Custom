#ifndef W12_NATIVE_H
#define W12_NATIVE_H

#ifdef __cplusplus
extern "C" {
#endif

const char *w12_native_version(void);
int w12_native_restart_requested(void);
void w12_native_mark_restart(void);
int w12_native_clear_restart(void);
int w12_native_desktop_blur_supported(void);
int w12_native_wallpaper_slots(void);

#ifdef __cplusplus
}
#endif

#endif
