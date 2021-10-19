#version 440

#define NB 16
#define NB_VERTICES (NB * 2 * 3)

layout (lines) in;
layout (triangle_strip, max_vertices = NB_VERTICES) out;

uniform mat4 modelview;
uniform mat4 projection;

#define PI 3.1415926538

const float branch_thickness = 0.1;

in vec3 v_pos[];

out vec3 g_pos;
out vec3 g_normal;

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

// template<typename T, qualifier Q>
// GLM_FUNC_QUALIFIER mat<4, 4, T, Q> orientation
// (
// 	vec<3, T, Q> const& Normal,
// 	vec<3, T, Q> const& Up
// )
// {
// 	if(all(equal(Normal, Up, epsilon<T>())))
// 		return mat<4, 4, T, Q>(static_cast<T>(1));
//
// 	vec<3, T, Q> RotationAxis = cross(Up, Normal);
// 	T Angle = acos(dot(Normal, Up));
//
// 	return rotate(Angle, RotationAxis);
// }

mat4 orientation(vec3 dir, vec3 up) {
    vec3 rotation_axis = cross(up, dir);
    // float angle = acos(dot(dir, up));
    return calcRotateMat4(rotation_axis);
}

vec3 triangle_normal(vec3 p0, vec3 p1, vec3 p2) {
    return normalize(cross(p1 - p0, p2 - p0));
}

void main() {
    vec3 node = gl_in[0].gl_Position.xyz;
    vec3 node_parent = gl_in[1].gl_Position.xyz;

    vec3 dir = normalize(node_parent.xyz - node.xyz);

    mat4 rot = orientation(dir, vec3(0, 1, 0));

    mat4 translate_node = calcTranslateMat4(node);
    mat4 translate_node_parent = calcTranslateMat4(node_parent);



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

        vec3 a_normal = -triangle_normal(a0.xyz, a1.xyz, a2.xyz);

        gl_Position = projection * modelview * a0;
        g_normal = a_normal;
        EmitVertex();
        gl_Position = projection * modelview * a2;
        g_normal = a_normal;
        EmitVertex();
        gl_Position = projection * modelview * a1;
        g_normal = a_normal;
        EmitVertex();

        //triangle 2
        vec4 b1 = translate_node_parent * rot * p1;
        vec4 b2 = translate_node * rot * p2;
        vec4 b3 = translate_node_parent * rot * p2;

        vec3 b_normal = triangle_normal(b1.xyz, b2.xyz, b3.xyz);

        gl_Position = projection * modelview * b1;
        g_normal = b_normal;
        EmitVertex();
        gl_Position = projection * modelview * b3;
        g_normal = b_normal;
        EmitVertex();
        gl_Position = projection * modelview * b2;
        g_normal = b_normal;
        EmitVertex();

        g_pos = v_pos[i];

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
