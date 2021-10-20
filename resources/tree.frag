#version 430

layout(location=0) out vec4 out_color;
layout(location=1) out vec4 out_branch_color;

in vec3 g_position;
in vec3 g_normal;
in vec3 g_branch_color;

uniform vec3 lightPosition;
uniform vec2 resolution;

void main() {
    float intensity = dot(normalize(lightPosition), normalize(g_normal));
    // vec2 texel = gl_FragCoord.xy / resolution;

    float value = 1.0;
    if (intensity > 0.5)
        value = 1.0;
    else
        value = 0.4;

    // for adding noise to the color
    // vec3 color1 = vec3(0.4, 0.6, 0.0);
    // vec3 color2 = vec3(0.4, 0.3, 0.0);
    // float noise_value = snoise(vec3(texel*12.0, 1.0));
    // vec3 c = color1 + color2 * noise_value;

    out_branch_color = vec4(g_branch_color, 1.0);
    out_color = vec4(0.0, value, 0.0, 1.0);
}
