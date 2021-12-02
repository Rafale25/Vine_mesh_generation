#version 430

layout (location = 0) in vec4 in_glPos;
layout (location = 1) in vec3 in_pos;
layout (location = 2) in vec3 in_normal;
layout (location = 3) in int in_branch_color;

out vec3 v_position;
out vec3 v_normal;
flat out int v_branch_color;

void main() {
    gl_Position = in_glPos;
    v_position = in_pos;
    v_normal = in_normal;
    v_branch_color = in_branch_color;
}
