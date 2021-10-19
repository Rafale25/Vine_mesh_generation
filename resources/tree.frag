#version 430

layout(location=0) out vec4 out_color;
layout(location=1) out vec4 out_branch_color;

in vec3 g_position;
in vec3 g_normal;
in vec3 g_branch_color;

uniform vec3 lightPosition;

void main() {
    float intensity = dot(normalize(lightPosition), normalize(g_normal));

    float value = 1.0;
    if (intensity > 0.5)
        value = 1.0;
    else
        value = 0.4;

    out_branch_color = vec4(g_branch_color, 1.0);
    out_color = vec4(0.0, value, 0.0, 1.0);
}
