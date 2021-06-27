import sys,math, os;
from PIL import Image,ImagePalette;

FRAME_SIZE=(160,104)
sourceFolder=sys.argv[1];
#targetFolder=sys.argv[2];

def getFramesCount(source):
    count=0;
    for name in os.listdir(source):
        if os.path.isfile(source+os.sep+name):
            count+=1;
    return count;

def openFrame(source,id):
    return Image.open(source+os.sep+'%04d.png'%(id+1));

def diffBlock(screen,image,bx,by):
    different=False;
    blackCount=0;
    whiteCount=0;
    blockData=[];
    for y in range(8):
        pixelData=0;
        for x in range(8):
            pixelScreen=screen.getpixel((bx+x,by+y));
            pixelImage=image.getpixel((bx+x,by+y));
            if pixelScreen!=pixelImage:
                different=True;
            pixelData>>=1;
            if pixelImage>128:
                pixelData|=0x80;
                whiteCount+=1;
            else:
                blackCount+=1;
        blockData.append(pixelData);
    if not different:
        return None; #Use original content
    elif 0==whiteCount:
        return 1; #All black block
    elif 0==blackCount:
        return 2; #All white block
    else:
        return bytes(blockData); #Block with data

def diffFrame(screen,image):
    frameData=b'';
    for blockY in range(FRAME_SIZE[1]>>3):
        for blockX in range(FRAME_SIZE[0]>>3):
            addr=blockY*40+blockX;
            block=diffBlock(screen,image,blockX<<3,blockY<<3);
            if(None==block):
                pass;
            elif(1==block):
                frameData+=((addr|0x4000).to_bytes(2,'little'));
            elif(2==block):
                frameData+=((addr|0x8000).to_bytes(2,'little'));
            else:
                frameData+=(addr.to_bytes(2,'little')+block);
    return frameData;

def main():
    screen=Image.new('1',FRAME_SIZE,0);
    videoData=[];
    totalSize=0;
    try:
        for frameIdx in range(getFramesCount(sourceFolder)-1):
            print('Processing frame %d'%frameIdx);
            image=openFrame(sourceFolder,frameIdx);
            frameData=diffFrame(screen,image);
            videoData.append(frameData);
            totalSize+=len(frameData);
            screen.paste(image);
            image.close();
    except Exception as e:
        print(e);
    print('Estimated bytes of video data: %d'%totalSize);
    return 0;

#执行main方法，当C语言中的main()占坑用
exit(main());
