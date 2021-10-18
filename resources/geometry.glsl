#version 330

#if defined VERTEX_SHADER

uniform mat4 modelview;
uniform mat4 projection;

in vec3 in_vert;

out vec3 pos;

void main() {
    vec4 p = modelview * vec4(in_vert, 1.0);
    gl_Position = projection * p;
    pos = p.xyz;
}

#elif defined FRAGMENT_SHADER

layout(location=0) out vec4 out_position;

in vec3 pos;

void main() {
    out_position = vec4(pos, 0.0);
}
#endif
