#version 430

uniform mat4 modelview;
uniform mat4 projection;

layout (location = 0) in vec3 in_vert;

out vec3 v_pos;

void main() {
    vec4 pos = vec4(in_vert, 1.0);
    gl_Position = pos;
    v_pos = (modelview * pos).xyz;
}
