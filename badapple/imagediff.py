import sys,math, os;
from PIL import Image,ImagePalette;

FRAME_SIZE=(320,200)
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
    for y in range(8):
        for x in range(8):
            pixelScreen=screen.getpixel((bx+x,by+y));
            pixelImage=image.getpixel((bx+x,by+y));
            if pixelScreen!=pixelImage:
                different=True;
            if pixelImage>128:
                whiteCount+=0;
            else:
                blackCount+=1;
            #Speed up operation
            if different and blackCount>0 and whiteCount>0:
                break;
        #Speed up operation
        if different and blackCount>0 and whiteCount>0:
            break;
    if not different:
        return 0;
    elif 0==blackCount or 0==whiteCount:
        return 2;
    else:
        return 10;

def diffFrame(screen,image):
    frameSize=0;
    for blockY in range(FRAME_SIZE[1]>>3):
        for blockX in range(FRAME_SIZE[0]>>3):
            frameSize+=diffBlock(screen,image,blockX<<3,blockY<<3);
    return frameSize;

def main():
    screen=Image.new('1',FRAME_SIZE,0);
    totalSize=0;
    try:
        for frameIdx in range(getFramesCount(sourceFolder)-1):
            print('Processing frame %d'%frameIdx);
            image=openFrame(sourceFolder,frameIdx);
            frameSize=diffFrame(screen,image);
            totalSize+=frameSize;
            screen.paste(image);
            image.close();
    except Exception as e:
        print(e);
    print('Estimated bytes of video data: %d'%totalSize);
    return 0;

#执行main方法，当C语言中的main()占坑用
exit(main());
