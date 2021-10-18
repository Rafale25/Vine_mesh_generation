#version 330

layout (triangles) in;
layout (line_strip, max_vertices = 6) out;

uniform mat4 modelview;
uniform mat4 projection;

in vec3 v_normal[];

// out vec3 g_color;

const float normal_scale = 0.1;

void main() {

    for (int i = 0 ; i < 3 ; ++i) {
        vec4 v0 = gl_in[i].gl_Position;
        gl_Position = projection * modelview * v0;
        EmitVertex();

        vec4 v1 = v0 + vec4(v_normal[i] * normal_scale, 0);
        gl_Position = projection * modelview * v1;
        EmitVertex();

        // if (i == 0)
        //     g_color = vec3(1.0, 0.0, 0.0);
        // if (i == 1)
		// 	g_color = vec3(0.0, 1.0, 0.0);
        // if (i == 2)
		// 	g_color = vec3(1.0, 0.0, 1.0);

        EndPrimitive();
    }

}
