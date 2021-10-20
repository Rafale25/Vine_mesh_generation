#version 430

out vec4 fragColor;

uniform vec3 lightPosition;
uniform vec2 resolution;

uniform float near;
uniform float far;

uniform sampler2D texture0; // color
uniform sampler2D texture1; // depth
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

float color_difference(vec3 c1, vec3 c2) {
    return distance(c1, c2);
}

void main() {
    vec2 texel = gl_FragCoord.xy / resolution;

    vec3 color = texture(texture0, texel).rgb;
    // float depth = texture(texture1, texel).r;

    float value = 1.0;

    vec3 color_center = texture(texture2, texel).rgb;
    vec3 color_right = texture_at(texture2, texel, vec2(2, 0)).rgb;
    vec3 color_bot = texture_at(texture2, texel, vec2(0, 2)).rgb;

    if (color_difference(color_center, color_right) > 0.001 ||
        color_difference(color_center, color_bot) > 0.001)
        value = 0.0;

    // float d = get_dist_at(texture1, texel, 2);
    // float diff = d - depth;
    // if (diff > 0.001)
        // value = 0.0;

    fragColor = vec4(color*value, 1.0);
}

// if (intensity > 0.95)
//     value = 1.0;
// else if (intensity > 0.75)
//     value = 0.8;
// else if (intensity > 0.50)
//     value = 0.6;
// else if (intensity > 0.25)
//     value = 0.4;
// else
//     value = 0.2;
