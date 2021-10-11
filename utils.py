from math import pi, cos, sin, sqrt
from random import uniform
from glm import vec3

# def random_uniform_vec2():
# 	angle = uniform(-math.pi, math.pi);
# 	return cos(angle), sin(angle);

def random_uniform_vec3():
	x, y, z = uniform(-1, 1), uniform(-1, 1), uniform(-1, 1)
	mag = sqrt(x*x + y*y + z*z)
	return vec3(x/mag, y/mag, z/mag);

def degToRad(angle):
	return angle * (math.pi / 180.0)

def read_file(path):
	data = None
	with open(path, 'r') as file:
		data = file.read()
	return data

def fclamp(x, min_x, max_x):
	return (max(min(x, max_x), min_x))
