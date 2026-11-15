/* OoT-MouseCapture.exe: the native-camera mouse helper on its own, for people who start the emulator themselves.
   Start it before or after the game; it waits for the game window, works only while the game is in front, and
   quits when the game closes. See mouse_capture.h for what it does. */
#include "mouse_capture.h"

#pragma comment(lib, "kernel32.lib")

static volatile LONG stop_flag = 0;

static void print_status(const wchar_t *msg) {
    SYSTEMTIME t;
    GetLocalTime(&t);
    wprintf(L"[%02d:%02d:%02d] %ls\n", t.wHour, t.wMinute, t.wSecond, msg);
}

static BOOL WINAPI on_console(DWORD type) {
    (void)type;
    InterlockedExchange(&stop_flag, 1);
    mc_release();                        /* closing this window gives the normal mouse settings back */
    return TRUE;
}

int main(void) {
    /* one copy at a time (it may also be started by Windows at logon) */
    HANDLE once = CreateMutexW(NULL, TRUE, L"Local\\OoT-MouseCapture-helper");
    if (once && GetLastError() == ERROR_ALREADY_EXISTS) {
        wprintf(L"The OOT mouse helper is already running (look for its window in the taskbar). Nothing to do.\n");
        Sleep(3000);
        return 0;
    }
    SetConsoleCtrlHandler(on_console, TRUE);
    setvbuf(stdout, NULL, _IONBF, 0);          /* show each line at once */
    {   /* --data <folder>: Lichii's data folder (settings, qt-config.ini); started by Apply-Settings from a private copy */
        int argc = 0;
        wchar_t **argv = CommandLineToArgvW(GetCommandLineW(), &argc);
        for (int i = 1; argv && i + 1 < argc; i++)
            if (wcscmp(argv[i], L"--data") == 0) {
                wcsncpy(mc_config_dir, argv[i + 1], MAX_PATH - 1);
                mc_config_dir[MAX_PATH - 1] = 0;
            }
    }
    mc_logfile_open();
    wprintf(L"OOT mouse helper (native mouse camera)\n\n"
            L"It starts by itself with Windows and waits for the game: you do not need to do anything.\n"
            L"It only acts while the game is in front; Alt+Tab gives the normal mouse back at any time.\n"
            L"Close this window to stop it (it comes back at the next logon).\n\n");
    mc_log = print_status;
    for (;;) {                                  /* one round per game start; the helper itself keeps running */
        mc_say(L"Waiting for the game window... Start the game if you have not.");
        McFind f = {0, NULL};
        while (!f.top && !stop_flag) {
            EnumWindows(mc_find_top, (LPARAM)&f);
            if (!f.top) Sleep(500);
        }
        if (stop_flag) return 0;
        DWORD pid = 0;
        GetWindowThreadProcessId(f.top, &pid);
        wchar_t title[256] = L"", exe[MAX_PATH] = L"?", msg[700];
        DWORD n = MAX_PATH;
        HANDLE p = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
        if (p) {
            QueryFullProcessImageNameW(p, 0, exe, &n);
            CloseHandle(p);
        }
        GetWindowTextW(f.top, title, 256);
        swprintf(msg, 700, L"Game found: %ls  (%ls)", title, exe);
        mc_say(msg);
        mc_run(pid, &stop_flag);
        if (stop_flag) break;
        mc_say(L"Game closed. Mouse settings are back to normal. Waiting for the next start.");
    }
    return 0;
}
