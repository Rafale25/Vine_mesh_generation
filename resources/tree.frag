#version 430

in vec3 v_normal;

out vec4 out_color;

void main() {
	// out_color = vec4(0.0, gl_FragCoord.z, v_normal.x*0.001, 1.0);
	out_color = vec4(v_normal*10.0, 1.0);
}
