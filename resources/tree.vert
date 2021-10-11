#version 430

uniform mat4 mvp; // modelview + projection

in vec3 in_vert;

// instanced data
in vec3 in_pos;

void main() {
	vec4 pos = mvp * vec4(in_vert + in_pos, 1.0);

	gl_PointSize = 2.0;
	gl_Position = pos;
}
