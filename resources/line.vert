#version 430

uniform mat4 modelview;
uniform mat4 projection;

in vec3 in_vert;

void main() {
	vec4 pos = projection * modelview * vec4(in_vert, 1.0);

	// gl_PointSize = 2.0;
	gl_Position = pos;
}
