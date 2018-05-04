import gi, re;
gi.require_version('Wnck', '3.0');
from gi.repository import Wnck, Gdk, GdkX11;

class WindowGrabber:
    @staticmethod
    def getWindowByTitle(regexp):
        result = [];
        screen = Wnck.Screen.get_default();
        screen.force_update();
        for win in screen.get_windows():
            if re.match(regexp, win.get_name()):
                result.append(win);
        return result;

    def __init__(self, wnckWindow):
        self.screen = GdkX11.X11Display.get_default();
        self.wnckWindow = wnckWindow;
        self.window = GdkX11.X11Window.foreign_new_for_display(self.screen, self.wnckWindow.get_xid());
        (self.x, self.y, self.w, self.h) = self.window.get_geometry();

    def capture(self):
        return Gdk.pixbuf_get_from_window(self.window, self.x, self.y, self.w, self.h);

