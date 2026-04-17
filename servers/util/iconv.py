import codecs
from util.tcpserver import ReaderWrapper,WriterWrapper


class IConvState:
    def __init__(self,enabled):
        self.enabled=enabled

class IConvStreamReader(ReaderWrapper):
    def __init__(self,reader,state,clientEnc,serverEnc):
        super().__init__(reader)
        self._decoder=codecs.getincrementaldecoder(clientEnc)(errors='surrogateescape')
        self._state,self.__serverEnc=state,serverEnc

    async def read(self,n=-1):
        text=''
        while not text:
            data = await super().read(n)
            if not data or not self._state.enabled:
                return data
            text = self._decoder.decode(data, final=False)
        raw = text.encode(self.__serverEnc, errors='ignore')
        return raw

class IConvStreamWriter(WriterWrapper):
    def __init__(self,writer,state,clientEnc,serverEnc):
        super().__init__(writer)
        self._decoder=codecs.getincrementaldecoder(serverEnc)(errors='surrogateescape')
        self._state,self.__clientEnc=state,clientEnc

    def write(self,chunk):
        if not self._state.enabled:
            super().write(chunk)
            return
        text=self._decoder.decode(chunk, final=False)
        raw=text.encode(self.__clientEnc,errors='ignore')
        super().write(raw)


def IConvWrapper(reader,writer,clientEnc,serverEnc='utf-8',enabled=True):
    if clientEnc is None or serverEnc is None or clientEnc==serverEnc:
        return reader,writer
    state=IConvState(enabled)
    readerIconv=IConvStreamReader(reader,state,clientEnc,serverEnc)
    writerIconv=IConvStreamWriter(writer,state,clientEnc,serverEnc)
    return readerIconv,writerIconv

