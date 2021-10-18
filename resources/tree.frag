#version 430

in vec3 g_normal;
in vec3 g_pos;

layout(location=0) out vec4 out_depth;
// layout(location=1) out vec4 out_position;
// out vec4 fragColor;

uniform vec3 lightPosition;
// uniform vec2 resolution;

// uniform float near;
// uniform float far;

// depth texture
// uniform sampler2D texture0;

// float linear_depth(float z) {
//     return (2.0 * near) / (far + near - z * (far - near));
// }
//
// float texture_at(vec2 uv, vec2 offset) {
//     offset /= resolution;
//     return linear_depth(texture(texture0, uv + offset).r);
// }
//
// float get_dist_at(vec2 texel, float m) {
//     float d = 0.0;
//     d = max(d, texture_at(texel, vec2(1*m, 0*m)));
//     d = max(d, texture_at(texel, vec2(-1*m, 0*m)));
//     d = max(d, texture_at(texel, vec2(0*m, 1*m)));
//     d = max(d, texture_at(texel, vec2(0*m, -1*m)));
//
//     d = max(d, texture_at(texel, vec2(1*m, 1*m)));
//     d = max(d, texture_at(texel, vec2(-1*m, -1*m)));
//     d = max(d, texture_at(texel, vec2(1*m, -1*m)));
//     d = max(d, texture_at(texel, vec2(-1*m, 1*m)));
//
//     return d;
// }

void main() {
    float intensity = dot(normalize(lightPosition), normalize(g_normal));

    float value = 1.0;
    if (intensity > 0.5)
        value = 1.0;
    else
        value = 0.4;

    // vec2 texel = gl_FragCoord.xy / resolution;
    // float z = texture(texture0, texel).r;
    //
    // float d = get_dist_at(texel, 2);
    //
    // float diff = d - z;
    //
    // if (diff > 0.001)
    //     value = 0.0;

    // out_color = vec4(0.0, value, 0.0, 1.0);
    // out_position = vec4(1.0, 0.0, 0.0, 0.0);
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
