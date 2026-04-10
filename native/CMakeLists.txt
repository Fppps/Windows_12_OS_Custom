cmake_minimum_required(VERSION 3.16)
project(w12native C)

add_library(w12native SHARED
    src/w12_native_core.c
    src/w12_window_effects.c
    src/w12_wallpaper_fx.c
)

target_include_directories(w12native PUBLIC include)
set_target_properties(w12native PROPERTIES OUTPUT_NAME "w12native")
