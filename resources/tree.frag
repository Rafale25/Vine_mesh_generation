#version 430

in vec3 v_normal;

out vec4 fragColor;

uniform vec3 lightPosition;
uniform vec3 view_direction;

void main() {
    float intensity = dot(normalize(lightPosition), v_normal);

    float value = intensity;

    // if (intensity > 0.5)
    //     value = 1.0;
    // else
    //     value = 0.4;

    if (dot(v_normal, view_direction) <= 0.2)
        value = value*0.999;
        // value = 0.0;

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
    // out_color = vec4(v_normal * gl_FragCoord.z, 1.0);
}
