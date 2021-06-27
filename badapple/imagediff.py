import sys,math, os;
from PIL import Image,ImagePalette;

FRAME_SIZE=(320,200)
sourceFolder=sys.argv[1];
targetFolder=sys.argv[2];

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
    imageBlockArr=[];
    blockImage=Image.new('P',(8,8),2);
    blockImage.putpalette(bytes((0,0,0,255,255,255,255,0,255)),'RGB');
    for y in range(8):
        for x in range(8):
            pixelScreen=screen.getpixel((bx+x,by+y));
            pixelImage=image.getpixel((bx+x,by+y));
            if pixelScreen!=pixelImage:
                different=True;
            if pixelImage>128:
                blockImage.putpixel((x,y),1);
            else:
                blockImage.putpixel((x,y),0);
    if not different:
        return None;
    else:
        return blockImage;

def diffFrame(screen,image):
    result=Image.new('P',FRAME_SIZE,2);
    result.putpalette(bytes((0,0,0,255,255,255,255,0,255)),'RGB');
    for blockY in range(FRAME_SIZE[1]>>3):
        for blockX in range(FRAME_SIZE[0]>>3):
            diffBlockResult=diffBlock(screen,image,blockX<<3,blockY<<3);
            if diffBlockResult:
                result.paste(diffBlockResult,(blockX<<3,blockY<<3));
                diffBlockResult.close();
    return result;

def main():
    screen=Image.new('1',FRAME_SIZE,0);
    for frameIdx in range(getFramesCount(sourceFolder)):
        print('Processing frame %d'%frameIdx);
        image=openFrame(sourceFolder,frameIdx);
        diffImage=diffFrame(screen,image);
        diffImage.save(targetFolder+os.sep+'%04d.png'%(frameIdx+1),'PNG');
        diffImage.close();
        screen.paste(image);
        image.close();

    return 0;

#执行main方法，当C语言中的main()占坑用
exit(main());
