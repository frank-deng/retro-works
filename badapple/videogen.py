import sys,math, os;
from PIL import Image,ImagePalette;

FRAME_SIZE=(160,104)
sourceFolder=sys.argv[1];
targetFile=sys.argv[2];
reportFile=sys.argv[3];

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
    blockDataEven=[];
    for y in range(8):
        pixelData=0;
        for x in range(8):
            pixelScreen=screen.getpixel((bx+x,by+y));
            pixelImage=image.getpixel((bx+x,by+y));
            if pixelScreen!=pixelImage:
                different=True;
            if pixelImage>128:
                pixelData|=1;
                whiteCount+=1;
            else:
                blackCount+=1;
            if x<7:
                pixelData<<=1;
        if y&1:
            blockDataEven.append(pixelData);
        else:
            blockData.append(pixelData);
    blockData+=blockDataEven;
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
    blockXCount=FRAME_SIZE[0]>>3;
    blockYCount=FRAME_SIZE[1]>>3;
    for blockY in range(blockYCount):
        for blockX in range(blockXCount):
            addr=(blockY+6)*40*4+(blockX+10);
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

def getFrameOffset(allFrames,frameIdx):
    offset=len(allFrames)*6+2+4;
    for frame in allFrames[0:frameIdx]:
        offset+=len(frame);
    return offset;

def main():
    screen=Image.new('1',FRAME_SIZE,0);
    frameData=[];
    try:
        for frameIdx in range(getFramesCount(sourceFolder)):
            print('Processing frame %d'%frameIdx);
            image=openFrame(sourceFolder,frameIdx);
            frameData.append(diffFrame(screen,image));
            screen.paste(image);
            image.close();
    except Exception as e:
        print(e);

    print('Generate data file');
    frameMetaData=b'';
    with open(reportFile,'w') as fpreport:
        for frameIdx in range(len(frameData)):
            length=len(frameData[frameIdx]);
            if 0==length:
                offset=0;
            else:
                offset=getFrameOffset(frameData,frameIdx);
            frameMetaData+=(length.to_bytes(2,'little')+offset.to_bytes(4,'little'));
            fpreport.write('Frame %d at offset %x length %d\n'%(frameIdx,offset,length));

    with open(targetFile,'wb') as fp:
        fp.write(b'BA\x00\x00'+len(frameData).to_bytes(2,'little')+frameMetaData+b''.join(frameData));

    return 0;

#执行main方法，当C语言中的main()占坑用
exit(main());
