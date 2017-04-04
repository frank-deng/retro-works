try:
    import msvcrt;
    def getch():
        ch = msvcrt.getch();
        if ch == '\x00' or ord(ch)>=0xA1:
            return ch+msvcrt.getch();
        else:
            return ch;
except ImportError:
    import tty, sys, termios;
    def getch():
        fd = sys.stdin.fileno();
        old_settings = termios.tcgetattr(fd);
        try:
            tty.setraw(sys.stdin.fileno());
            ch = sys.stdin.read(1);
            if ch == '\x00' or ord(ch)>=0xA1:
                return ch+sys.stdin.read(1);
            else:
                return ch;
        except Exception as e:
            pass;
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings);
        return None;

