#version 440

#define PI 3.1415926538

#define NB_FACES -1 // get changed when loaded
#define NB_SEGMENTS -1 // get changed when loaded
#define CYLINDER_INCREMENT (PI*2.0 / NB_FACES)
#define NB_VERTICES (NB_FACES * 2*3)

layout (triangles_adjacency) in;
layout (triangle_strip, max_vertices = NB_VERTICES) out;
layout (invocations = NB_SEGMENTS) in;

out vec3 g_position;
out vec3 g_normal;
flat out int g_branch_color;

uniform mat4 modelview;
uniform mat4 projection;

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

void output_segment(vec3 node1, vec3 node2, vec3 dir1, vec3 dir2, float radius1, float radius2) {
    float yaw1 = atan(dir1.z, dir1.x);
    float pitch1 = atan(sqrt(dir1.z * dir1.z + dir1.x * dir1.x), dir1.y) + PI;

    float yaw2 = atan(dir2.z, dir2.x);
    float pitch2 = atan(sqrt(dir2.z * dir2.z + dir2.x * dir2.x), dir2.y) + PI;

    // mat4 ror_reverse = calcRotateMat4Y(PI);
    // mat4 rot_node = calcRotateMat4(vec3(0.0, yaw1, pitch1)) * ror_reverse;

    mat4 rot_node = calcRotateMat4(vec3(0.0, yaw1, pitch1));
    mat4 rot_parent = calcRotateMat4(vec3(0.0, yaw2, pitch2));

    mat4 translate_node = calcTranslateMat4(node1);
    mat4 translate_node_parent = calcTranslateMat4(node2);

    mat4 mvp = projection * modelview;

    for (int i = 0 ; i < NB_FACES ; ++i) {
        const float angle1 = CYLINDER_INCREMENT * i;
        const float angle2 = CYLINDER_INCREMENT * (i + 1);

        float x1 = cos(angle1);
        float z1 = sin(angle1);

        float x2 = cos(angle2);
        float z2 = sin(angle2);

        const vec3 p1 = vec3(x1, 0.0, z1);
        const vec3 p2 = vec3(x2, 0.0, z2);

        vec4 p1_node = vec4(p1 * radius1, 1.0);
        vec4 p1_parent = vec4(p1 * radius2, 1.0);

        vec4 p2_node = vec4(p2 * radius1, 1.0);
        vec4 p2_parent = vec4(p2 * radius2, 1.0);

        //triangle 1
        vec4 a0_r = rot_node * p1_node;
        vec4 a1_r = rot_parent * p1_parent;
        vec4 a2_r = rot_node * p2_node;

        vec4 a0 = translate_node * a0_r;
        vec4 a1 = translate_node_parent * a1_r;
        vec4 a2 = translate_node * a2_r;

        // g_normal = triangle_normal(a0.xyz, a2.xyz, a1.xyz);

        gl_Position = mvp * a0;
        g_normal = a0_r.xyz;
        g_position = a0.xyz;
        EmitVertex();
        gl_Position = mvp * a2;
        g_normal = a2_r.xyz;
        g_position = a2.xyz;
        EmitVertex();
        gl_Position = mvp * a1;
        g_normal = a1_r.xyz;
        g_position = a1.xyz;
        EmitVertex();

        //triangle 2
        vec4 b1_r = rot_parent * p1_parent;
        vec4 b2_r = rot_node * p2_node;
        vec4 b3_r = rot_parent * p2_parent;

        vec4 b1 = translate_node_parent * b1_r;
        vec4 b2 = translate_node * b2_r;
        vec4 b3 = translate_node_parent * b3_r;

        // g_normal = triangle_normal(b1.xyz, b2.xyz, b3.xyz);

        gl_Position = mvp * b1;
        g_normal = b1_r.xyz;
        g_position = b1.xyz;
        EmitVertex();
        gl_Position = mvp * b3;
        g_normal = b3_r.xyz;
        g_position = b3.xyz;
        EmitVertex();
        gl_Position = mvp * b2;
        g_normal = b2_r.xyz;
        g_position = b2.xyz;
        EmitVertex();

        EndPrimitive();
    }
}

// t: 0.0 -> 1.0
vec3 getSplinePoint(vec3 p0, vec3 p1, vec3 p2, vec3 p3, float t) {
    // t = t - int(t); // not used because t never goes above 1.0

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

    return vec3(tx, ty, tz) * 0.5;
}

vec3 getSplineGradient(vec3 p0, vec3 p1, vec3 p2, vec3 p3, float t) {
    // t = t - int(t); // not used because t never goes above 1.0

    float tt = t * t;
    float ttt = tt * t;

    float q1 = -3.0*tt + 4.0*t - 1.0;
    float q2 = 9.0*tt - 10.0*t;
    float q3 = -9.0*tt + 8.0*t + 1.0;
    float q4 = 3.0*tt - 2.0*t;

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

    return vec3(tx, ty, tz) * 0.5;
}

int packColor(vec3 color) {
    int r = 65536 * int(color.r*255);
    int g = 256 * int(color.g*255);
    int b = int(color.b*255);

    return int(r + g + b);
}

void main() {
    vec3 node = gl_in[0].gl_Position.xyz;
    vec3 node_parent = gl_in[1].gl_Position.xyz;

    vec3 parent_parent = gl_in[2].gl_Position.xyz;
    vec3 node_child = gl_in[3].gl_Position.xyz;

    float parent_radius = gl_in[4].gl_Position.x;
    float node_radius = gl_in[4].gl_Position.y;
    float body_id = gl_in[4].gl_Position.z;

    int i = gl_InvocationID.x;

    const float increment = 1.0 / NB_SEGMENTS;
    float t1 = increment * i;
    float t2 = increment * (i + 1);

    vec3 p1 = getSplinePoint(parent_parent, node_parent, node, node_child, t1);
    vec3 p2 = getSplinePoint(parent_parent, node_parent, node, node_child, t2);

    vec3 p1_dir = getSplineGradient(parent_parent, node_parent, node, node_child, t1);
    vec3 p2_dir = getSplineGradient(parent_parent, node_parent, node, node_child, t2);

    // vec3 dir = normalize(p1 - p2);
    // g_branch_color = packColor(hsv2rgb(vec3( rand(vec2(dir)), 1.0, 1.0)));
    g_branch_color = packColor(hsv2rgb(vec3( body_id*74.24982, 1.0, 1.0)));

    float radius1 = mix(parent_radius, node_radius, t1);
    float radius2 = mix(parent_radius, node_radius, t2);

    output_segment(p1, p2, p1_dir, p2_dir, radius1, radius2);
}

/*
1 - 3 - 5
| \ | \ |
0 - 2 - 4
#indices for NB_FACES=3 ; GL_TRIANGLES
0 2 1
1 2 3

2 4 3
3 4 5
*/
