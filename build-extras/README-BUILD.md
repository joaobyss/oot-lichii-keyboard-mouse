# How the v1.4.7 files were built

Everything here is the source of what is in `OoT-KeyboardMouse-v1_4_7.zip`.

## Game patch (`MouseCamera-Native`, an IPS for game version 2.0.0)
    cd native-camera/patch
    clang -O1 -w test_cave.c cave.c -o test_cave -lm && ./test_cave        # PC test, must print ALL OK
    python3 build_native_camera_ips.py --llvm /usr/lib/llvm-18/bin --out out   # clang/lld for AArch64
The shipped `.ips.off` was built with clang 18 (Ubuntu). `cave.c` has a speed-aware unwrap (`unwrap_fast`),
so fast turns are less likely to be mistaken for pointer wrap corrections;
`WRAP_X/WRAP_Y` must match `MC_WRAP_X/MC_WRAP_Y` in `helper/mouse_capture.h`.

## Helper (`OoT-MouseCapture.exe`)
    cd native-camera/helper
    x86_64-w64-mingw32-gcc -O2 -static -mconsole -Wall -Wno-unknown-pragmas -D_CRT_SECURE_NO_WARNINGS \
        -o OoT-MouseCapture.exe mouse_capture.c -luser32 -lwinmm -lshell32 -ladvapi32
(`build.bat` does the same with Visual Studio.) The helper can start at logon, waits for the game, writes
`OoT-MouseCapture-log.txt` beside the settings, uses a high-resolution timer when Windows supports it, and hides/restores
the system cursor while it owns the game mouse.

## Settings program (`OoT-KeyboardMouse-Config.exe`)
The program is the unchanged v1.4.x PyInstaller exe; only the files inside it were replaced:
    python3 build-extras/patch_exe.py OoT-KeyboardMouse-Config.exe NEW.exe \
      'payload\OoT-MouseCapture.exe=OoT-MouseCapture.exe' \
      'payload\Apply-Settings.ps1=settings/Apply-Settings.ps1' \
      'payload\OoT-Keyboard-Mouse-Settings.ini=settings/OoT-Keyboard-Mouse-Settings.ini' \
      'payload\load\0400486024DEC000\MouseCamera-Native\exefs\E0F3CCFAF50065AE4EA01EB5AEB13B1A45DA3348.ips.off=<built .ips>'
(needs `pip install pyinstaller` only to read the archive; the script rewrites the TOC and cookie itself.)

## Simulation used to pick the unwrap limits
`build-extras/simhand.py`, `sim2.py`: minimum-jerk hand strokes, 1 ms helper wrap, HID sample every 16/33 ms.
