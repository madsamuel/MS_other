#version 330

layout(location = 0) in vec3 vertex;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 texCoord;

uniform mat4 p3d_ModelViewProjectionMatrix;

out vec3 v_normal;

void main() {
    v_normal = normal;
    gl_Position = p3d_ModelViewProjectionMatrix * vec4(vertex, 1.0);
}
