#version 120

// Simple scanlines with curvature and mask effects lifted from crt-lottes
// by hunterk

////////////////////////////////////////////////////////////////////
////////////////////////////  SETTINGS  ////////////////////////////
/////  comment these lines to disable effects and gain speed  //////
////////////////////////////////////////////////////////////////////

#define CURVATURE // applies barrel distortion to the screen
#define OVERSCAN_X 0.1
#define OVERSCAN_Y 0.1
#define CURVATURE_SMOOTH 0.001

////////////////////////////////////////////////////////////////////
//////////////////////////  END SETTINGS  //////////////////////////
////////////////////////////////////////////////////////////////////

///////////////////////  Runtime Parameters  ///////////////////////
#pragma parameter warpX "warpX" 0.031 0.0 0.125 0.01
#pragma parameter warpY "warpY" 0.041 0.0 0.125 0.01

#if defined(VERTEX)

#if __VERSION__ >= 130
#define COMPAT_VARYING out
#define COMPAT_ATTRIBUTE in
#define COMPAT_TEXTURE texture
#else
#define COMPAT_VARYING varying
#define COMPAT_ATTRIBUTE attribute
#define COMPAT_TEXTURE texture2D
#endif

#ifdef GL_ES
#define COMPAT_PRECISION mediump
#else
#define COMPAT_PRECISION
#endif

COMPAT_ATTRIBUTE vec4 a_position;
COMPAT_ATTRIBUTE vec4 COLOR;
COMPAT_ATTRIBUTE vec4 TexCoord;
COMPAT_VARYING vec4 COL0;
COMPAT_VARYING vec2 v_texCoord;

vec4 _oPosition1;
uniform mat4 MVPMatrix;
uniform COMPAT_PRECISION int FrameDirection;
uniform COMPAT_PRECISION int rubyFrameCount;
uniform COMPAT_PRECISION vec2 rubyOutputSize;
uniform COMPAT_PRECISION vec2 rubyTextureSize;
uniform COMPAT_PRECISION vec2 rubyInputSize;

// compatibility #defines
#define vTexCoord v_texCoord.xy
#define SourceSize vec4(rubyTextureSize, 1.0 / rubyTextureSize) //either rubyTextureSize or rubyInputSize
#define OutSize vec4(rubyOutputSize, 1.0 / rubyOutputSize)

#ifdef PARAMETER_UNIFORM
uniform COMPAT_PRECISION float WHATEVER;
#else
#define WHATEVER 0.0
#endif

void main()
{
	gl_Position = a_position;
	//v_texCoord = vec2(a_position.x + 1.0, 1.0 - a_position.y) / 2.0 * rubyInputSize / rubyTextureSize;
	v_texCoord = vec2((a_position.x + 1.0 - OVERSCAN_X) / (2.0 - OVERSCAN_X*2), (1.0 - OVERSCAN_Y - a_position.y) / (2.0 - OVERSCAN_Y*2)) * rubyInputSize / rubyTextureSize;
}

#elif defined(FRAGMENT)

#if __VERSION__ >= 130
#define COMPAT_VARYING in
#define COMPAT_TEXTURE texture
out vec4 FragColor;
#else
#define COMPAT_VARYING varying
#define FragColor gl_FragColor
#define COMPAT_TEXTURE texture2D
#endif

#ifdef GL_ES
#ifdef GL_FRAGMENT_PRECISION_HIGH
precision highp float;
#else
precision mediump float;
#endif
#define COMPAT_PRECISION mediump
#else
#define COMPAT_PRECISION
#endif

uniform COMPAT_PRECISION int FrameDirection;
uniform COMPAT_PRECISION int rubyFrameCount;
uniform COMPAT_PRECISION vec2 rubyOutputSize;
uniform COMPAT_PRECISION vec2 rubyTextureSize;
uniform COMPAT_PRECISION vec2 rubyInputSize;
uniform sampler2D rubyTexture;
COMPAT_VARYING vec2 v_texCoord;

// compatibility #defines
#define Source rubyTexture
#define vTexCoord v_texCoord.xy

#define SourceSize vec4(rubyTextureSize, 1.0 / rubyTextureSize) //either rubyTextureSize or rubyInputSize
#define OutSize vec4(rubyOutputSize, 1.0 / rubyOutputSize)

#ifdef PARAMETER_UNIFORM
uniform COMPAT_PRECISION float warpX;
uniform COMPAT_PRECISION float warpY;
#else
#define warpX 0.031
#define warpY 0.041
#endif

/*
	The following code allows the shader to override any texture filtering
	configured in DOSBox. if 'output' is set to 'opengl', bilinear filtering
	will be enabled and OPENGLNB will not be defined, if 'output' is set to
	'openglnb', nearest neighbour filtering will be enabled and OPENGLNB will
	be defined.

	If you wish to use the default filtering method that is currently enabled
	in DOSBox, use COMPAT_TEXTURE to lookup a texel from the input texture.

	If you wish to force nearest-neighbor interpolation use NN_TEXTURE.

	If you wish to force bilinear interpolation use BL_TEXTURE.

	If DOSBox is configured to use the filtering method that is being forced,
	the default	hardware implementation will be used, otherwise the custom
	implementations below will be used instead.

	These custom implemenations rely on the `rubyTextureSize` uniform variable.
	The code could calculate the texture size from the sampler using the
	textureSize() GLSL function, but this would require a minimum of GLSL
	version 130, which may prevent the shader from working on older systems.
*/

#if defined(OPENGLNB)
#define NN_TEXTURE COMPAT_TEXTURE
#define BL_TEXTURE blTexture
vec4 blTexture(in sampler2D sampler, in vec2 uv)
{
	// subtract 0.5 here and add it again after the floor to centre the texel
	vec2 texCoord = uv * rubyTextureSize - vec2(0.5);
	vec2 s0t0 = floor(texCoord) + vec2(0.5);
	vec2 s0t1 = s0t0 + vec2(0.0, 1.0);
	vec2 s1t0 = s0t0 + vec2(1.0, 0.0);
	vec2 s1t1 = s0t0 + vec2(1.0);

	vec2 invTexSize = 1.0 / rubyTextureSize;
	vec4 c_s0t0 = COMPAT_TEXTURE(sampler, s0t0 * invTexSize);
	vec4 c_s0t1 = COMPAT_TEXTURE(sampler, s0t1 * invTexSize);
	vec4 c_s1t0 = COMPAT_TEXTURE(sampler, s1t0 * invTexSize);
	vec4 c_s1t1 = COMPAT_TEXTURE(sampler, s1t1 * invTexSize);

	vec2 weight = fract(texCoord);

	vec4 c0 = c_s0t0 + (c_s1t0 - c_s0t0) * weight.x;
	vec4 c1 = c_s0t1 + (c_s1t1 - c_s0t1) * weight.x;

	return (c0 + (c1 - c0) * weight.y);
}
#else
#define BL_TEXTURE COMPAT_TEXTURE
#define NN_TEXTURE nnTexture
vec4 nnTexture(in sampler2D sampler, in vec2 uv)
{
	vec2 texCoord = floor(uv * rubyTextureSize) + vec2(0.5);
	vec2 invTexSize = 1.0 / rubyTextureSize;
	return COMPAT_TEXTURE(sampler, texCoord * invTexSize);
}
#endif

#ifdef CURVATURE
// Distortion of scanlines, and end of screen alpha.
vec2 Warp(vec2 pos)
{
	pos  = pos*2.0-1.0;
	pos *= vec2(1.0 + (pos.y*pos.y)*warpX, 1.0 + (pos.x*pos.x)*warpY);

	return pos*0.5 + 0.5;
}
#endif

void main()
{
#ifdef CURVATURE
	vec2 posNorm=v_texCoord.xy*(rubyTextureSize.xy/rubyInputSize.xy);
	vec2 pos = Warp(posNorm)*(rubyInputSize.xy/rubyTextureSize.xy);
#else
	vec2 pos = v_texCoord.xy;
#endif

	FragColor = BL_TEXTURE(Source, pos);

//Remove garbled display around
#if defined CURVATURE
	float left=Warp(vec2(1, posNorm.y)).x-1;
	float right=Warp(vec2(0, posNorm.y)).x+0.999;
	float top=Warp(vec2(posNorm.x,1)).y-1;
	float bottom=Warp(vec2(posNorm.x,0)).y+0.999;
	float alpha=max(max(
		smoothstep(-CURVATURE_SMOOTH,0,left-posNorm.x),
		smoothstep(0,CURVATURE_SMOOTH,posNorm.x-right)
	),max(
		smoothstep(-CURVATURE_SMOOTH,0,top-posNorm.y),
		smoothstep(0,CURVATURE_SMOOTH,posNorm.y-bottom)
	));
	FragColor=mix(FragColor,vec4(0,0,0,1),alpha);
#else
	if(v_texCoord.x <= 0 || v_texCoord.x >= (rubyInputSize.x/rubyTextureSize.x)
		|| v_texCoord.y <= 0 || v_texCoord.y >= (rubyInputSize.y/rubyTextureSize.y)){
		FragColor = vec4(0.0,0,0,1.0);
	}
#endif
}
#endif
