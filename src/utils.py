from math import pi, cos, sin, sqrt
from random import uniform

import glm

def easeOutCirc(x):
    return sqrt(1.0 - pow(x - 1.0, 2.0));

# def random_uniform_vec2():
# 	angle = uniform(-math.pi, math.pi);
# 	return cos(angle), sin(angle);

def triangle_normal(p0, p1, p2):
	return glm.normalize(glm.cross(p1-p0, p2-p0))

def random_uniform_vec3():
	x, y, z = uniform(-1, 1), uniform(-1, 1), uniform(-1, 1)
	mag = sqrt(x*x + y*y + z*z)
	return glm.vec3(x/mag, y/mag, z/mag);

def degToRad(angle):
	return angle * (math.pi / 180.0)

def read_file(path):
	data = None
	with open(path, 'r') as file:
		data = file.read()
	return data

def fclamp(x, min_x, max_x):
	return (max(min(x, max_x), min_x))

# print all attributes and methods of object in console
def dump(obj):
	for attr in dir(obj):
		print("obj.%s = %r" % (attr, getattr(obj, attr)))
