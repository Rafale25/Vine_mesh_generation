#version 430

#define PI 3.1415926538

layout(location=0) out vec4 out_color;

in vec2 f_texCoord;

uniform sampler2D texture0;
// uniform vec3 lightPosition;

float rand(vec2 co){
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

float map(float value, float min1, float max1, float min2, float max2) {
    return min2 + (value - min1) * (max2 - min2) / (max1 - min1);
}

void main() {
    // float intensity = dot(normalize(lightPosition), normalize(g_normal));
    //
    // float value = intensity;
    // if (intensity > 0.5)
    //     value = 1.0;
    // else
    //     value = 0.4;
    // value = value*0.001 + intensity;

    // for adding noise to the color

    // vec3 color = vec3(1.0, 0.0, 0.0);;
    // out_color = vec4(color, 1.0);
    vec4 color = texture(texture0, f_texCoord);
    out_color = color;
}
