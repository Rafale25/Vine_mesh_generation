#version 330

layout (lines) in;
layout (line_strip, max_vertices = 2) out;

uniform mat4 modelview;
uniform mat4 projection;

const float normal_scale = 0.1;

void main() {
    vec4 v0 = projection * modelview * gl_in[0].gl_Position;
    EmitVertex();

    vec4 v1 = projection * modelview * gl_in[1].gl_Position;
    EmitVertex();

    EndPrimitive();
}

// for (int i = 0 ; i < 3 ; ++i) {
//     vec4 v0 = gl_in[i].gl_Position;
//     gl_Position = projection * modelview * v0;
//     EmitVertex();
//
//     vec4 v1 = v0 + vec4(v_normal[i] * normal_scale, 0);
//     gl_Position = projection * modelview * v1;
//     EmitVertex();
//
//     EndPrimitive();
// }
