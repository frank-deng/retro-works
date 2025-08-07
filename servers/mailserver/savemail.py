import asyncio,datetime,os

async def run(userName,params,recvQueue,sendQueue):
    while True:
        msgInfo=await recvQueue.get()
        try:
            now=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            target_dir=params.get('path','.')
            filepath=f"{target_dir}{os.sep}email_{now}.eml"
            with open(filepath,'wb') as fp:
                fp.write(msgInfo['msg'])
        except:
            print_exc()
