#version 430

uniform sampler2D texture0;

in vec2 uv;

out vec4 fragColor;

void main() {
	vec3 color = texture(texture0, uv).rgb;

	fragColor = vec4(color, 1.0);
}
