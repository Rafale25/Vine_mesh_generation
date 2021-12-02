#version 430

uniform mat4 modelview;
uniform mat4 projection;

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec3 in_texcoord_0;

void main() {
    vec4 pos = vec4(in_position, 1.0);
    gl_Position = pos;
}
