#ifndef __timer_h__
#define __timer_h__

#include "wav.h"

void initTimer(wav_t* wav);
void closeTimer();
int waitTimer(unsigned int cycles);

#endif
