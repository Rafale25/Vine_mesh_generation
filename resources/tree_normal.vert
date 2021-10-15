#version 430

uniform mat4 mvp; // modelview + projection

layout (location = 0) in vec3 in_vert;
layout (location = 1) in vec3 in_normal;

out vec3 v_normal;
// out VS_GS_VERTEX
// {
//     vec2 UV;
//     vec3 vs_worldpos;
//     vec3 vs_normal;
// } vertex_out;

void main() {
	gl_Position = vec4(in_vert, 1.0);
	v_normal = in_normal;
}
