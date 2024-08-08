varying float vWobble;
uniform vec3 uColorA;
uniform vec3 uColorB;

void main()
{
    float colorMix = smoothstep(-1.0, 1.0, vWobble);
    csm_DiffuseColor.rgb = mix(uColorA, uColorB, colorMix);
}