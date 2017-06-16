#version 330 core

in vec2 TexCoord;
in vec3 Normal;
in vec3 FragPos;

out vec4 outColor;

uniform sampler2D diffuse;
uniform sampler2D specular;
uniform sampler2D emission;

uniform vec3 viewPos;

struct Material {
    float shininess;
};

uniform Material material;

struct DirLight {
    vec3 direction;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

vec4 CalcDirLight(DirLight light, vec3 normal, vec3 viewDir)
{
    vec3 lightDir = normalize(-light.direction);

    //diffuse
    float diff = max(dot(normal, lightDir), 0.0);
    //specular
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);

    //net
    vec4 ambient = vec4(light.ambient, 1.0) * texture(diffuse, TexCoord);
    vec4 diffuse = vec4(light.diffuse, 1.0) * diff * texture(diffuse, TexCoord);
    vec4 specular = vec4(light.specular, 1.0) * spec * texture(specular, TexCoord);
    return (ambient + diffuse + specular);
}

uniform DirLight dirLight;

struct PointLight {
    vec3 position;

    float constant;
    float linear;
    float quadratic;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

vec4 CalcPointLight(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir)
{
    vec3 lightDir = normalize(light.position - fragPos);

    //diffuse
    float diff = max(dot(normal, lightDir), 0.0);
    //specular
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);

    //attenuation
    float distance = length(light.position - fragPos);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));

    //net
    vec4 ambient  = vec4(light.ambient, 1.0)  * texture(diffuse, TexCoord);
    vec4 diffuse  = vec4(light.diffuse, 1.0)  * diff * texture(diffuse, TexCoord);
    vec4 specular = vec4(light.specular, 1.0) * spec * texture(specular, TexCoord);
    ambient  *= attenuation;
    diffuse  *= attenuation;
    specular *= attenuation;
    return (ambient + diffuse + specular);
}

void main()
{
    //properties
    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);

    //Directional
    vec4 result = CalcDirLight(dirLight, norm, viewDir);

    //outColor = result;
    outColor = texture(diffuse, TexCoord);
}