#version 440

#define NB 32
#define NB_VERTICES (NB * 2 * 3)

layout (lines) in;
layout (triangle_strip, max_vertices = NB_VERTICES) out;

uniform mat4 modelview;
uniform mat4 projection;

#define PI 3.1415926538

const float branch_thickness = 0.1;

out vec3 g_normal;

mat4 rotation3d(vec3 axis, float angle) {
    axis = normalize(axis);
    float s = sin(angle);
    float c = cos(angle);
    float oc = 1.0 - c;

    return mat4(
        c * axis.x * axis.x + c,           oc * axis.x * axis.y - axis.z * s,  oc * axis.z * axis.x + axis.y * s,  0.0,
        oc * axis.x * axis.y + axis.z * s,  oc * axis.y * axis.y + c,           oc * axis.y * axis.z - axis.x * s,  0.0,
        oc * axis.z * axis.x - axis.y * s,  oc * axis.y * axis.z + axis.x * s,  oc * axis.z * axis.z + c,           0.0,
        0.0,                                0.0,                                0.0,                                1.0
    );
}

vec3 triangle_normal(vec3 p0, vec3 p1, vec3 p2) {
    return normalize(cross(p1 - p0, p2 - p0));
}

void main() {
    vec3 node = gl_in[0].gl_Position.xyz;
    vec3 node_parent = gl_in[1].gl_Position.xyz;

    vec3 dir = normalize(node_parent.xyz - node.xyz);

    float pitch = asin(-dir.y);
    float yaw = atan(dir.x, dir.z);

    mat4 rot_y = rotation3d(vec3(0, 1, 0), yaw);
    mat4 rot_x = rotation3d(vec3(1, 0, 0), pitch);
    mat4 rot = rot_y * rot_x;

    for (int i = 0 ; i < NB ; ++i) {
        float angle1 = (PI*2.0 / NB) * i;
        float angle2 = (PI*2.0 / NB) * (i + 1);

        float x1 = cos(angle1) * branch_thickness;
        float z1 = sin(angle1) * branch_thickness;

        float x2 = cos(angle2) * branch_thickness;
        float z2 = sin(angle2) * branch_thickness;

        vec3 p1 = vec3(x1, 0, z1);
        vec3 p2 = vec3(x2, 0, z2);

        //triangle 1
        vec3 a0 = (rot * vec4(p1, 1.0)).xyz + node;
        vec3 a1 = (rot * vec4(p1, 1.0)).xyz + node_parent;
        vec3 a2 = (rot * vec4(p2, 1.0)).xyz + node;

        vec3 a_normal = -triangle_normal(a0, a1, a2);

        gl_Position = projection * modelview * vec4(a0, 1.0);
        g_normal = a_normal;
        EmitVertex();
        gl_Position = projection * modelview * vec4(a2, 1.0);
        g_normal = a_normal;
        EmitVertex();
        gl_Position = projection * modelview * vec4(a1, 1.0);
        g_normal = a_normal;
        EmitVertex();

        //triangle 2
        vec3 b1 = (rot * vec4(p1, 1.0)).xyz + node_parent;
        vec3 b2 = (rot * vec4(p2, 1.0)).xyz + node;
        vec3 b3 = (rot * vec4(p2, 1.0)).xyz + node_parent;

        vec3 b_normal = triangle_normal(b1, b2, b3);

        gl_Position = projection * modelview * vec4(b1, 1.0);
        g_normal = b_normal;
        EmitVertex();
        gl_Position = projection * modelview * vec4(b3, 1.0);
        g_normal = b_normal;
        EmitVertex();
        gl_Position = projection * modelview * vec4(b2, 1.0);
        g_normal = b_normal;
        EmitVertex();


        EndPrimitive();
    }
}

// for j, node in enumerate(self.tree.nodes):
//     dir = glm.sub(node.parent.pos, node.pos)
//
//     mat_translate_parent = glm.translate(glm.mat4(), node.parent.pos)
//     mat_translate_self = glm.translate(glm.mat4(), node.pos)
//     mat_rotate = glm.orientation(dir, vec3(0,1,0))
//
//     for i in range(NB):
//         angle1 = (PI*2.0 / NB) * i
//         angle2 = (PI*2.0 / NB) * (i + 1)
//
//         x1 = cos(angle1) * branch_thickness
//         z1 = sin(angle1) * branch_thickness
//
//         x2 = cos(angle2) * branch_thickness
//         z2 = sin(angle2) * branch_thickness
//
//         p1 = vec4(x1, 0, z1, 1.0)
//         p2 = vec4(x2, 0, z2, 1.0)
//
//         # triangle 1
//         a0 = mat_translate_self * mat_rotate * p1
//         a1 = mat_translate_parent * mat_rotate * p1
//         a2 = mat_translate_self * mat_rotate * p2
//
//         a_normal = triangle_normal(a0.xyz, a1.xyz, a2.xyz)
//
//         data.extend(a0.xyz)
//         data.extend(a_normal) # one for each of the 3 vertices
//
//         data.extend(a1.xyz)
//         data.extend(a_normal)
//
//         data.extend(a2.xyz)
//         data.extend(a_normal)
//
//         # triangle 2
//         b1 = mat_translate_parent * mat_rotate * p1
//         b3 = mat_translate_self * mat_rotate * p2
//         b2 = mat_translate_parent * mat_rotate * p2
//
//         b_normal = triangle_normal(b1.xyz, b2.xyz, b3.xyz)
//
//         data.extend(b1.xyz)
//         data.extend(b_normal)
//
//         data.extend(b2.xyz)
//         data.extend(b_normal)
//
//         data.extend(b3.xyz)
//         data.extend(b_normal)

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
