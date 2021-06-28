#ifndef __frame_h__
#define __frame_h__

#define FRAME_WIDTH 160
#define FRAME_HEIGHT 104

unsigned char initFrame();
void closeFrame();
unsigned int getFrameCount();
unsigned int getFrameData(unsigned char *buffer, unsigned int frameIdx);

#endif
