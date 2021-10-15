#version 330

layout (triangles) in;
layout (line_strip, max_vertices = 6) out;

// layout (points) in;
// layout (line_strip, max_vertices = 2) out;

uniform mat4 mvp;

in vec3 v_normal[];

// VS_GS_VERTEX
// in gl_PerVertex
// {
//     vec3 pos;
//     vec3 normal;
// } gl_in[];

const float normal_scale = 0.1;

void main() {

    for (int i = 0 ; i < 3 ; ++i) {
        vec4 v0 = gl_in[i].gl_Position;
        gl_Position = mvp * v0;
        EmitVertex();

        vec4 v1 = v0 + vec4(v_normal[i] * normal_scale, 0);
        gl_Position = mvp * v1;
        EmitVertex();

        EndPrimitive();
    }

}
