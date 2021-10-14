#version 430

uniform mat4 mvp; // modelview + projection

layout (location = 0) in vec3 in_vert;
layout (location = 1) in vec3 in_normal;

out vec3 v_normal;

void main() {
	vec4 pos = mvp * vec4(in_vert, 1.0);

	gl_Position = pos;
	// v_normal =  (normalize(in_normal) * 0.5f) + 0.5f;
	v_normal =  normalize(in_normal);
}
