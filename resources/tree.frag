#version 430

out vec4 out_color;

void main() {
	out_color = vec4(0.0, gl_FragCoord.z, 0.0, 1.0);
}
