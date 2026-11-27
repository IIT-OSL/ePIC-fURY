#!/usr/bin/env python3
"""Keep an X window sized to fill its X screen (for Isaac Sim inside a rootful Xwayland with no window manager).

Usage: DISPLAY=:2 python3 tools/x_fit_window.py ["Isaac Sim"] [--once]
Polls once a second; when the X screen size changes (outer Xwayland window resized / fullscreen), moves the
matching top-level window to 0,0 and resizes it to the screen. Only sends XMoveResizeWindow; nothing else.
"""
import ctypes, ctypes.util, sys, time

x11 = ctypes.cdll.LoadLibrary(ctypes.util.find_library("X11"))
x11.XOpenDisplay.restype = ctypes.c_void_p
x11.XDefaultRootWindow.restype = ctypes.c_ulong
x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]

class XWA(ctypes.Structure):  # XWindowAttributes, only the leading fields we read
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int), ("width", ctypes.c_int), ("height", ctypes.c_int),
                ("pad", ctypes.c_char * 256)]

def name_of(d, w):
    p = ctypes.c_char_p()
    if x11.XFetchName(ctypes.c_void_p(d), ctypes.c_ulong(w), ctypes.byref(p)) and p.value:
        return p.value.decode(errors="replace")
    return ""

def find(d, root, title):
    r, parent, kids, n = ctypes.c_ulong(), ctypes.c_ulong(), ctypes.POINTER(ctypes.c_ulong)(), ctypes.c_uint()
    x11.XQueryTree(ctypes.c_void_p(d), ctypes.c_ulong(root), ctypes.byref(r), ctypes.byref(parent), ctypes.byref(kids), ctypes.byref(n))
    for i in range(n.value):
        if title in name_of(d, kids[i]):
            return kids[i]
    return None

def geom(d, w):
    a = XWA()
    x11.XGetWindowAttributes(ctypes.c_void_p(d), ctypes.c_ulong(w), ctypes.byref(a))
    return a.x, a.y, a.width, a.height

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    title = args[0] if args else "Isaac Sim"
    once = "--once" in sys.argv
    d = x11.XOpenDisplay(None)
    if not d:
        sys.exit("cannot open DISPLAY")
    root = x11.XDefaultRootWindow(d)
    last = None
    while True:
        _, _, rw, rh = geom(d, root)
        w = find(d, root, title)
        if w:
            g = geom(d, w)
            if g != (0, 0, rw, rh) and (rw, rh, w) != last:
                x11.XMoveResizeWindow(ctypes.c_void_p(d), ctypes.c_ulong(w), 0, 0, rw, rh)
                x11.XFlush(ctypes.c_void_p(d))
                print(f"[x_fit] {time.strftime('%H:%M:%S')} '{title}' {g[2]}x{g[3]} -> {rw}x{rh}", flush=True)
                last = (rw, rh, w)
        if once:
            break
        time.sleep(1.0)

if __name__ == "__main__":
    main()
