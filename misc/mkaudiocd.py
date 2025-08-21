#!/usr/bin/env python3
# Install dependencies: pip install audioread
import sys, subprocess, os, getopt, re, audioread;
from glob import glob;

def sec2timestr(sec):
    return '%02u:%02u:%02u' % (int(int(sec) / 60), int(sec) % 60, int(75 * (sec % 1)));

def writeCue(duration, targetCue, targetAudio):
    totalSec = 0;
    idx = 0;
    with open(targetCue, 'w') as f:
        f.write("FILE \"%s\" %s\n" % (targetAudio, 'FLAC'));
        for sec in duration:
            f.write("  TRACK %02u AUDIO\n" % (idx + 1));
            f.write("    INDEX 01 %s\n" % (sec2timestr(totalSec)));
            totalSec += sec;
            idx += 1;

if __name__ == '__main__':
    targetCue='audiocd.cue';
    targetAudio='audiocd.flac';
    opts, args = getopt.getopt(sys.argv[1:], 'o:');
    for k,v in opts:
        if (k == '-o'):
            targetCue = v+'.cue';
            targetAudio = v+'.flac';

    files = [];
    duration = [];
    for arg in args:
        for fname in glob(arg):
            with audioread.audio_open(fname) as f:
                duration.append(f.duration);
                files.append(fname);
    
    if len(files) == 0:
        sys.stderr.write("No audio file found.\n");
        exit(1);

    try:
        writeCue(duration, targetCue, targetAudio);
    except Exception as e:
        sys.stderr.write(str(e) + "\n");
        exit(1);

    params = ['ffmpeg'];
    filter_complex = '';
    idx = 0;
    for f in files:
        params.append('-i');
        params.append(f);
        filter_complex += '[%u:0]' % idx;
        idx += 1;
    filter_complex += 'concat=n=%u:v=0:a=1[out]' % idx;
    params += ['-filter_complex', filter_complex, '-map', '[out]', targetAudio];
    proc = subprocess.Popen(params);
    exit(proc.wait());
