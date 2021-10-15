#version 430

uniform mat4 mvp;

layout (location = 0) in vec3 in_vert;
layout (location = 1) in vec3 in_normal;

// smooth out vec3 v_position;
out vec3 FragPos;
out vec3 v_normal;

void main() {
	vec4 pos = mvp * vec4(in_vert, 1.0);

	FragPos = in_vert;
	gl_Position = pos;
	v_normal =  normalize(in_normal);
}
