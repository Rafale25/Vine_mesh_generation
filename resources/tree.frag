#version 430

in vec3 v_normal;
in vec3 FragPos;

out vec4 fragColor;

uniform vec3 lightPosition;
uniform vec2 resolution;

uniform float near;
uniform float far;

uniform sampler2D texture0;

float linear_depth(float z) {
    return (2.0 * near) / (far + near - z * (far - near));
}

float texture_at(vec2 uv, vec2 offset) {
    offset /= resolution;
    return linear_depth(texture(texture0, uv + offset).r);
}

float get_dist_at(vec2 texel, float m) {
    float d = 0.0;
    d = max(d, texture_at(texel, vec2(1*m, 0*m)));
    d = max(d, texture_at(texel, vec2(-1*m, 0*m)));
    d = max(d, texture_at(texel, vec2(0*m, 1*m)));
    d = max(d, texture_at(texel, vec2(0*m, -1*m)));

    d = max(d, texture_at(texel, vec2(1*m, 1*m)));
    d = max(d, texture_at(texel, vec2(-1*m, -1*m)));
    d = max(d, texture_at(texel, vec2(1*m, -1*m)));
    d = max(d, texture_at(texel, vec2(-1*m, 1*m)));

    return d;
}

void main() {
    float intensity = dot(normalize(lightPosition), normalize(v_normal));
    // vec3 dir = normalize(-view_position - FragPos);

    float value = 1.0;
    if (intensity > 0.5)
        value = 1.0;
    else
        value = 0.4;

    vec2 texel = gl_FragCoord.xy / resolution;
    float z = texture(texture0, texel).r;

    float d = 0.0;
    for (int i = 0 ; i < 3 ; ++i) {
        d += get_dist_at(texel, i);
    }
    // d /= 4;

    float diff = d - z;

    if (diff > 0.1)
        value = 0.0;

    // if ( dot(v_normal, dir) <= 0.5)
    //     value = 0.0;

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

    fragColor = vec4(0.0, value, 0.0, 1.0);
    // fragColor = vec4(0.0, clamp(intensity, 0.2, 1.0) * gl_FragCoord.z, 0.0, 1.0);
    // fragColor = vec4(v_normal * gl_FragCoord.z, 1.0);
    // fragColor = vec4(0.0, 1.0, 0.0, 1.0);
}
