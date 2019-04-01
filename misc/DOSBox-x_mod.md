Modification for `dosbox-x`:

`src/gui/render_template.h`:

	393 #define SCALERNAME    NormalDh
	394 #define SCALERWIDTH   1
	395 #define SCALERHEIGHT  2
	396 #define SCALERFUNC                \
	397 {                         \
	398   Bitu halfpixel=(((P & redblueMask) * 4) >> 3) & redblueMask;  \
	399   halfpixel|=(((P & greenMask) * 4) >> 3) & greenMask;      \
	400   line0[0]=P;           \
	401   line1[0]=halfpixel;             \
	402 }
	403 #include "render_simple.h"
	404 #undef SCALERNAME
	405 #undef SCALERWIDTH
	406 #undef SCALERHEIGHT
	407 #undef SCALERFUNC
	408 
	409 #if (DBPP > 8)
	410 
	411 #if RENDER_USE_ADVANCED_SCALERS>0
	412 
	413 #define SCALERNAME    TV2x
	414 #define SCALERWIDTH   2
	415 #define SCALERHEIGHT  2
	416 #define SCALERFUNC                  \
	417 {                         \
	418   Bitu halfpixel=(((P & redblueMask) * 4) >> 3) & redblueMask;  \
	419   halfpixel|=(((P & greenMask) * 4) >> 3) & greenMask;      \
	420   line0[0]=halfpixel;             \
	421   line0[1]=halfpixel;             \
	422   line1[0]=P;           \
	423   line1[1]=P;           \
	424 }
	425 #include "render_simple.h"
	426 #undef SCALERNAME
	427 #undef SCALERWIDTH
	428 #undef SCALERHEIGHT
	429 #undef SCALERFUNC

`src/hardware/vga_other.cpp`:

	272 static Bit8u cga16_val = 0;
	273 static void update_cga16_color(void);
	274 static Bit8u herc_pal = 0;
	275 static Bit8u mono_cga_pal = 3;
	276 static Bit8u mono_cga_bright = 1;


