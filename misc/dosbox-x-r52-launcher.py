#!/usr/bin/env python3
import subprocess, time;
xres, yres = 1024, 768;

dosbox = subprocess.Popen(['dosbox-x'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL);

import gi, re;
gi.require_version('Wnck', '3.0');
from gi.repository import Wnck, Gdk, GdkX11;

# Get DOSBox-X window
windowMatch = r'DOSBox-X';
dosboxWindow = None;
wnckScreen = Wnck.Screen.get_default();
wnckScreen.force_update();
for win in wnckScreen.get_windows():
    if re.match(windowMatch, win.get_name()):
        dosboxWindow = win;
        break;

if (None == dosboxWindow):
    print("DOSBox-X not running.");
    exit(1);

screen = GdkX11.X11Display.get_default();
window = GdkX11.X11Window.foreign_new_for_display(screen, dosboxWindow.get_xid());

try:
    x0, y0, w0, h0 = window.get_geometry();
    xt, yt = (xres-w0)/2, (yres-h0)/2;
    window.move(xt, yt);
    from pykeyboard import PyKeyboard;
    kbd = PyKeyboard();
    kbd.press_key(kbd.control_r_key);
    kbd.press_key(kbd.function_keys[10]);
    time.sleep(0.1);
    kbd.release_key(kbd.function_keys[10]);
    kbd.release_key(kbd.control_r_key);

    while None == dosbox.poll():
        x, y, w, h = window.get_geometry();
        xt, yt = (xres-w)/2, (yres-h)/2;
        dummy, x, y = window.get_origin();
        if (w == w0 and h == h0 and x == xt and y == yt):
            time.sleep(1/60);
            continue;
        w0, h0 = w, h;
        window.move(xt, yt);
except KeyboardInterrupt:
    pass;
exit(0);

