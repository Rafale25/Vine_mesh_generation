#version 440

#define NB 32
#define NB_SEGMENTS 8
#define NB_VERTICES (NB * 2*3)

// layout (lines) in;
layout (lines_adjacency) in;
layout (triangle_strip, max_vertices = NB_VERTICES) out;
layout(invocations = NB_SEGMENTS) in;

uniform mat4 modelview;
uniform mat4 projection;

#define PI 3.1415926538

const float branch_thickness = 0.1;

out vec3 g_position;
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

void output_segment(vec3 p1, vec3 p2) {
    vec3 dir = normalize(p2 - p1);
    float yaw = atan(dir.z, dir.x);
    float pitch = atan(sqrt(dir.z * dir.z + dir.x * dir.x), dir.y) + PI;

    mat4 rot = calcRotateMat4(vec3(0.0, yaw, pitch));
    mat4 translate_node = calcTranslateMat4(p1);
    mat4 translate_node_parent = calcTranslateMat4(p2);



    // g_branch_color = hsv2rgb(vec3(rand(vec2(dir.x + index, dir.y)), 1.0, 1.0));
    // g_branch_color = bcolor;

    mat4 mvp = projection * modelview;

    for (int i = 0 ; i < NB ; ++i) {
        float angle1 = (PI*2.0 / NB) * i;
        float angle2 = (PI*2.0 / NB) * (i + 1);

        float x1 = cos(angle1) * branch_thickness;
        float z1 = sin(angle1) * branch_thickness;

        float x2 = cos(angle2) * branch_thickness;
        float z2 = sin(angle2) * branch_thickness;

        vec4 p1 = vec4(x1, 0.0, z1, 1.0);
        vec4 p2 = vec4(x2, 0.0, z2, 1.0);

        //triangle 1
        vec4 a0 = translate_node * rot * p1;
        vec4 a1 = translate_node_parent * rot * p1;
        vec4 a2 = translate_node * rot * p2;

        g_normal = triangle_normal(a0.xyz, a2.xyz, a1.xyz);

        gl_Position = mvp * a0;
        g_position = a0.xyz;
        EmitVertex();
        gl_Position = mvp * a2;
        g_position = a2.xyz;
        EmitVertex();
        gl_Position = mvp * a1;
        g_position = a1.xyz;
        EmitVertex();

        //triangle 2
        vec4 b1 = translate_node_parent * rot * p1;
        vec4 b2 = translate_node * rot * p2;
        vec4 b3 = translate_node_parent * rot * p2;

        g_normal = triangle_normal(b1.xyz, b2.xyz, b3.xyz);

        gl_Position = mvp * b1;
        g_position = b1.xyz;
        EmitVertex();
        gl_Position = mvp * b3;
        g_position = b3.xyz;
        EmitVertex();
        gl_Position = mvp * b2;
        g_position = b2.xyz;
        EmitVertex();

        EndPrimitive();
    }
}

// t: 0.0 -> 1.0
vec3 getSplinePoint(vec3 p0, vec3 p1, vec3 p2, vec3 p3, float t) {
    t = t - int(t);

    float tt = t * t;
    float ttt = tt * t;

    float q1 = -ttt + 2.0*tt - t;
    float q2 = 3.0*ttt - 5.0*tt + 2.0;
    float q3 = -3.0*ttt + 4.0*tt +t;
    float q4 = ttt - tt;

    float tx = p0.x * q1 +
               p1.x * q2 +
               p2.x * q3 +
               p3.x * q4;

    float ty = p0.y * q1 +
               p1.y * q2 +
               p2.y * q3 +
               p3.y * q4;

    float tz = p0.z * q1 +
               p1.z * q2 +
               p2.z * q3 +
               p3.z * q4;

    return vec3(tx * 0.5, ty * 0.5, tz * 0.5);
}

void main() {
    vec3 node = gl_in[0].gl_Position.xyz;
    vec3 node_parent = gl_in[1].gl_Position.xyz;

    vec3 parent_parent = gl_in[2].gl_Position.xyz;
    vec3 node_child = gl_in[3].gl_Position.xyz;

    g_branch_color = hsv2rgb(vec3(rand(vec2(node.x, node.y)), 1.0, 1.0));
    // g_branch_color = hsv2rgb(vec3( rand(vec2(dir)), 1.0, 1.0));

    int i = gl_InvocationID.x;
    // for (int i = 0 ; i < NB_SEGMENTS ; ++i) {
        float t1 = (1.0 / NB_SEGMENTS) * (i + 0);
        float t2 = clamp((1.0 / NB_SEGMENTS) * (i + 1), 0.0, 0.999);

        vec3 p1 = getSplinePoint(parent_parent, node_parent, node, node_child, t1);
        vec3 p2 = getSplinePoint(parent_parent, node_parent, node, node_child, t2);

        vec3 dir = normalize(p1 - p2);
        // g_branch_color = hsv2rgb(vec3( rand(vec2(dir)), 1.0, 1.0));

        output_segment(p1, p2);
    // }
}

/*
1 - 3 - 5
| \ | \ |
0 - 2 - 4
#indices for NB=3 ; GL_TRIANGLES
0 2 1
1 2 3

2 4 3
3 4 5
*/
