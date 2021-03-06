#version 430

out vec4 fragColor;

uniform vec3 lightPosition;
uniform vec2 resolution;

uniform float outline_visibility;
uniform int outline_thickness;

uniform float near;
uniform float far;

uniform sampler2D texture0; // color
// uniform sampler2D texture1; // depth
uniform sampler2D texture2; // branch_color

float linear_depth(float z) {
    return (2.0 * near) / (far + near - z * (far - near));
}

vec3 texture_at(sampler2D tex, vec2 uv, vec2 offset) {
    offset /= resolution;
    return texture(tex, uv + offset).rgb;
}

float texture_at_linear(sampler2D tex, vec2 uv, vec2 offset) {
    offset /= resolution;
    return linear_depth(texture(tex, uv + offset).r);
}

float get_dist_at(sampler2D tex, vec2 texel, float m) {
    float d = 0.0;
    d = max(d, texture_at_linear(tex, texel, vec2(1*m, 0*m)));
    d = max(d, texture_at_linear(tex, texel, vec2(-1*m, 0*m)));
    d = max(d, texture_at_linear(tex, texel, vec2(0*m, 1*m)));
    d = max(d, texture_at_linear(tex, texel, vec2(0*m, -1*m)));

    d = max(d, texture_at_linear(tex, texel, vec2(1*m, 1*m)));
    d = max(d, texture_at_linear(tex, texel, vec2(-1*m, -1*m)));
    d = max(d, texture_at_linear(tex, texel, vec2(1*m, -1*m)));
    d = max(d, texture_at_linear(tex, texel, vec2(-1*m, 1*m)));

    return d;
}

void main() {
    vec2 texel = gl_FragCoord.xy / resolution;

    vec3 color = texture(texture0, texel).rgb;
    // float depth = texture(texture1, texel).r;

    float value = 1.0;

    // branch color; for outline
    vec3 color_center = texture(texture2, texel).rgb;
    vec3 color_right = texture_at(texture2, texel, vec2(outline_thickness, 0)).rgb;
    vec3 color_bot = texture_at(texture2, texel, vec2(0, outline_thickness)).rgb;
    // vec3 color_rb = texture_at(texture2, texel, vec2(1, 1)).rgb;

    if (distance(color_center, color_right) > 0.001 ||
        distance(color_center, color_bot) > 0.001)
        // color_difference(color_center, color_rb) > 0.001)
        value = outline_visibility;

    fragColor = vec4(color*value, 1.0);
}
