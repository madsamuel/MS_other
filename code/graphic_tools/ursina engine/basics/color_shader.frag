#version 330

in vec3 v_normal;
out vec4 fragColor;

void main() {
    vec3 color = normalize(v_normal) * 0.5 + 0.5; // Use normal as color
    fragColor = vec4(color, 1.0);
}
