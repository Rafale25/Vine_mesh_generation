#version 430

in vec3 v_normal;
in vec3 FragPos;

out vec4 fragColor;

uniform vec3 lightPosition;
// uniform vec3 view_direction;
uniform vec3 view_position;

void main() {
    float intensity = dot(normalize(lightPosition), normalize(v_normal));
    vec3 dir = normalize(-view_position - FragPos);

    float value = 1.0;
    if (intensity > 0.5)
        value = 1.0;
    else
        value = 0.4;

    // α = arccos[(xa * xb + ya * yb + za * zb) / (√(xa2 + ya2 + za2) * √(xb2 + yb2 + zb2))]

    if ( dot(v_normal, dir) <= 0.5)
        value = 0.0;

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

    fragColor = vec4(0.0, value * gl_FragCoord.z, 0.0, 1.0);
    // fragColor = vec4(0.0, clamp(intensity, 0.2, 1.0) * gl_FragCoord.z, 0.0, 1.0);
    // fragColor = vec4(v_normal * gl_FragCoord.z, 1.0);
    // fragColor = vec4(0.0, 1.0, 0.0, 1.0);
}
