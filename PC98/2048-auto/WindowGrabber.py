# Install requirements: apt-get install python3-gi python3-xlib
import gi, re;
gi.require_version('Gdk','3.0');
from gi.repository import Gdk, GdkX11;

import Xlib
import Xlib.display
import time

class WindowGrabber:
    def __init__(self, regexp):
        self.regexp=re.compile(regexp);

    def capture(self):
        try:
            display = Xlib.display.Display()
            root = display.screen().root
            windowID = root.get_full_property(display.intern_atom('_NET_ACTIVE_WINDOW'), Xlib.X.AnyPropertyType).value[0]
            window = display.create_resource_object('window', windowID);
            if not self.regexp.match(window.get_wm_name()):
                return None;
            screen = GdkX11.X11Display.get_default();
            window = GdkX11.X11Window.foreign_new_for_display(screen,windowID);
            (x,y,w,h) = window.get_geometry();
            y = h-400;
            h = 400;
            return Gdk.pixbuf_get_from_window(window,x,y,w,h);
        except AttributeError:
            return None;
        except Xlib.error.BadWindow:
            return None;

