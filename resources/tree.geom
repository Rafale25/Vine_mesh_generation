#version 440

#define NB 8
#define NB_VERTICES (NB * 2 * 3)

layout (lines) in;
layout (triangle_strip, max_vertices = NB_VERTICES) out;

uniform mat4 modelview;
uniform mat4 projection;

#define PI 3.1415926538

const float branch_thickness = 0.1;

out vec3 g_normal;
out vec3 g_branch_color;

mat4 calcRotateMat4X(float radian) {
    return mat4(
        1.0, 0.0, 0.0, 0.0,
        0.0, cos(radian), -sin(radian), 0.0,
        0.0, sin(radian), cos(radian), 0.0,
        0.0, 0.0, 0.0, 1.0
    );
}

mat4 calcRotateMat4Y(float radian) {
    return mat4(
        cos(radian), 0.0, sin(radian), 0.0,
        0.0, 1.0, 0.0, 0.0,
        -sin(radian), 0.0, cos(radian), 0.0,
        0.0, 0.0, 0.0, 1.0
    );
}

mat4 calcRotateMat4Z(float radian) {
    return mat4(
        cos(radian), -sin(radian), 0.0, 0.0,
        sin(radian), cos(radian), 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    );
}

mat4 calcRotateMat4(vec3 radian) {
    return calcRotateMat4X(radian.x) * calcRotateMat4Y(radian.y) * calcRotateMat4Z(radian.z);
}

mat4 calcTranslateMat4(vec3 v) {
    return mat4(
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        v.x, v.y, v.z, 1.0
    );
}

mat4 orientation(vec3 dir, vec3 up) {
    vec3 rotation_axis = cross(up, dir);
    return calcRotateMat4(rotation_axis);
}

vec3 triangle_normal(vec3 p0, vec3 p1, vec3 p2) {
    return normalize(cross(p1 - p0, p2 - p0));
}

vec3 hsv2rgb(vec3 c) {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}

float rand(vec2 co){
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    vec3 node = gl_in[0].gl_Position.xyz;
    vec3 node_parent = gl_in[1].gl_Position.xyz;

    vec3 dir = normalize(node_parent.xyz - node.xyz);
    mat4 rot = orientation(dir, vec3(0, 1, 0));
    mat4 translate_node = calcTranslateMat4(node);
    mat4 translate_node_parent = calcTranslateMat4(node_parent);

    g_branch_color = hsv2rgb(vec3(rand(vec2(dir.x, dir.y)), 1.0, 1.0));

    for (int i = 0 ; i < NB ; ++i) {
        float angle1 = (PI*2.0 / NB) * i;
        float angle2 = (PI*2.0 / NB) * (i + 1);

        float x1 = cos(angle1) * branch_thickness;
        float z1 = sin(angle1) * branch_thickness;

        float x2 = cos(angle2) * branch_thickness;
        float z2 = sin(angle2) * branch_thickness;

        vec4 p1 = vec4(x1, 0, z1, 1.0);
        vec4 p2 = vec4(x2, 0, z2, 1.0);

        //triangle 1
        vec4 a0 = translate_node * rot * p1;
        vec4 a1 = translate_node_parent * rot * p1;
        vec4 a2 = translate_node * rot * p2;

        vec3 a_normal = triangle_normal(a0.xyz, a2.xyz, a1.xyz);

        g_normal = a_normal;
        gl_Position = projection * modelview * a0;
        EmitVertex();
        gl_Position = projection * modelview * a2;
        EmitVertex();
        gl_Position = projection * modelview * a1;
        EmitVertex();

        //triangle 2
        vec4 b1 = translate_node_parent * rot * p1;
        vec4 b2 = translate_node * rot * p2;
        vec4 b3 = translate_node_parent * rot * p2;

        vec3 b_normal = triangle_normal(b1.xyz, b2.xyz, b3.xyz);

        g_normal = b_normal;
        gl_Position = projection * modelview * b1;
        EmitVertex();
        gl_Position = projection * modelview * b3;
        EmitVertex();
        gl_Position = projection * modelview * b2;
        EmitVertex();

        EndPrimitive();
    }
}
