@echo off
wasm -fe=s16toat.err -fo=s16toa.obj s16toa\s16toat.asm
wasm -fe=1.err -fo=1.obj 1.asm
wlink @1.lnk > link.log

