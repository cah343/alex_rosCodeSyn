#!/usr/bin/env python

import yaml

#Function created a transform to convert the x and z velocities of a robot to another



scale = 1

with open("rosCodeSyn/config_files/yaml/"+"nao"+".yaml", 'r') as stream:
    try:
        nao_yaml = yaml.load(stream)
        #print(nao_yaml["linear"]["y"])
    except yaml.YAMLError as exc:
        print(exc)

x_upper_nao = nao_yaml["linear"]["x"]["upper"]
x_lower_nao = nao_yaml["linear"]["x"]["lower"]
z_upper_nao = nao_yaml["angular"]["z"]["upper"]
z_lower_nao = nao_yaml["angular"]["z"]["lower"]

with open("rosCodeSyn/config_files/yaml/jackal.yaml", 'r') as stream2:
    try:
        jackal_yaml = yaml.load(stream2)
        #print(jackal_yaml)
    except yaml.YAMLError as exc:
        print(exc)

x_upper_jackal = jackal_yaml["linear"]["x"]["upper"]
x_lower_jackal = jackal_yaml["linear"]["x"]["lower"]
z_upper_jackal = jackal_yaml["angular"]["z"]["upper"]
z_lower_jackal = jackal_yaml["angular"]["z"]["lower"]


print (x_upper_nao)
