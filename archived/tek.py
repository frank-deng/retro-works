import sys

class Tek4010Canvas:
    WIDTH=1024
    HEIGHT=780
    @staticmethod
    def __encode_pos(x,y):
        hix,lox=x>>5,x&0x1f
        hiy,loy=y>>5,y&0x1f
        return bytes([hiy+0x20,loy+0x60,hix+0x20,lox+0x40])
    
    def __init__(self,output=None,auto_flush=True):
        self._auto_flush=auto_flush
        self._output=sys.stdout.buffer
        if output is not None:
            self.change_output(output)

    def _write(self,data):
        self._output.write(data)
        if self._auto_flush:
            self.flush()

    def set_auto_flush(self,auto_flush):
        self._auto_flush=auto_flush

    def flush(self):
        self._output.flush()

    def change_output(self,output):
        self._output=output

    def switch_tek(self):
        self.clear()

    def switch_vt(self):
        self._write(b'\x18')

    def clear(self):
        self._write(b'\x1b\x0c')

    def moveto(self,x,y):
        self._write(b'\x1d'+self.__class__.__encode_pos(x,y))

    def lineto(self,x,y):
        self._write(self.__class__.__encode_pos(x,y))

