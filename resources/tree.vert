#version 430

uniform mat4 mvp; // modelview + projection

in vec3 in_vert;
in vec3 in_normal;

out vec3 v_normal;

void main() {
	vec4 pos = mvp * vec4(in_vert, 1.0);

	// gl_PointSize = 2.0;
	gl_Position = pos;
	v_normal = in_normal;
}
