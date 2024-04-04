from PyTracer import pyBVH, pyStructs, pyGeometry
from PySide2.QtGui import QVector3D
from PyTracer import pyStructs as st
from external_libraries.rayTracerPyWrapper.rayTracerPyWrapper import PyBindBVH, PyBindRay, PyBindRayInfo, PyBindPlane, PyBindPlaneInfo
import external_libraries.rayTracerPyWrapper.rayTracerPyWrapper as m
import numpy as np
import time
from helpers import geometry_loader

def build_cube(l):
	tr = []
	pr = []
	v0 = np.array([l, -l, l])
	v1 = np.array([l, -l, -l])
	v2 = np.array([-l, -l, l])
	v3 = np.array([-l, -l, -l])
	v4 = np.array([l, l, l])
	v5 = np.array([l, l, -l])
	v6 = np.array([-l, l, l])
	v7 = np.array([-l, l, -l])
	tr.append(st.Triangle(v0, v2, v1))
	tr.append(st.Triangle(v3, v1, v2))
	tr.append(st.Triangle(v1, v0, v5))
	tr.append(st.Triangle(v5, v0, v4))
	# tr.append(st.Triangle(v1, v5, v3))
	# tr.append(st.Triangle(v3, v5, v7))
	# tr.append(st.Triangle(v5, v6, v4))
	# tr.append(st.Triangle(v6, v5, v7))
	# tr.append(st.Triangle(v6, v7, v2))
	# tr.append(st.Triangle(v2, v7, v3))
	# tr.append(st.Triangle(v2, v0, v6))
	# tr.append(st.Triangle(v0, v4, v6))
	# pr.extend([v0, v2, v1, v3, v1, v2, v1, v0, v5, v5, v0, v4, v1, v5, v3, v3, v5, v7, v5, v6, v4, v6, v5, v7, v6, v7, v2, v2, v7, v3, v2, v0, v6, v0, v4, v6])
	pr.extend([v0, v2, v1, v3, v1, v2, v1, v0, v5, v5, v0, v4])
	return tr, pr

if __name__=="__main__":
	# print(dir(m))
	primitives = []
	triangles = []
	number_of_primitives = 100
	number_of_layers = 10
	number_of_rays = 1000

	# d = np.array([0.9848077, -0.17364822, 0.], dtype=np.float32)
	# o = np.array([-8.294405, 1.4625278, 11.], dtype=np.float32)
	# v0 = np.array([5.1702404, -0.91165304, -11.5], dtype=np.float32)
	# v1 = np.array([5.1702404, -0.91165304, 11.5], dtype=np.float32)
	# v2 = np.array([4.9930468, -1.6223392, 11.5], dtype=np.float32)
	# v3 = np.array([5.246802, -0.1832223, -11.5], dtype=np.float32)
	# t1 = st.Triangle(v0, v1, v2)
	# t0 = st.Triangle(v3, v1, v0)
	# ray = st.Ray(o, d)
	# info = st.RayIntersectionInfo()
	# print(t0.all_intersect64(ray, info), t1.all_intersect64(ray, info))
	# quit()
	# print("generating primitives")
	# start_time = time.time()
	# primitive_width = 1000
	# for i in range(number_of_primitives):
	# 	v0 = (np.random.rand(3) - 0.5) * primitive_width
	# 	v1 = (np.random.rand(3) - 0.5) * primitive_width
	# 	v2 = (np.random.rand(3) - 0.5) * primitive_width
	# 	triangles.append(st.Triangle(v0, v1, v2))
	# 	primitives.append(v0)
	# 	primitives.append(v1)
	# 	primitives.append(v2)
	#
	# filename = "../../resources/Bunny-LowPoly.obj"
	filename = "../../resources/closed_bunny_vn_centered.obj"
	# filename = "../../resources/EiffelTower_fixed.stl"
	# filename = "../../resources/cubeish.stl"
	# filename = "../../resources/dingding.stl"
	is_loaded, vertices_list, normals_list, bbox_min, bbox_max = geometry_loader.load_geometry(filename, False)
	if is_loaded:
		bunny = pyGeometry.PyGeometry(filename=filename, vertices=vertices_list, normals=normals_list,
											 bbox_min=bbox_min, bbox_max=bbox_max, use_bvh=True)

	bbox_width = bbox_max.x() - bbox_min.x()
	bbox_height = bbox_max.y() - bbox_min.y()
	bbox_depth = bbox_max.z() - bbox_min.z()
	width_offset = bbox_width / number_of_rays
	height_offset = bbox_height / number_of_layers
	c_total_time = 0
	p_total_time = 0
	c_single_total_time = 0
	# for l_idx in range(number_of_layers):
	#
	# 	rays_origins = [np.array([- bbox_width * 0.5 + width_offset * idx, -0.5 * bbox_height + height_offset * l_idx, bbox_depth]) for idx in
	# 					range(number_of_rays)]
	# 	rays_directions = [np.array([0, 0, -1]) for idx in range(number_of_rays)]
	# 	start_time = time.time()
	# 	rays = [pyStructs.Ray(rays_origins[idx], rays_directions[idx]) for idx in range(number_of_rays)]
	# 	rays_info = [pyStructs.RayIntersectionInfo() for _ in range(number_of_rays)]
	# 	_ = [bunny.get_bvh().all_intersections(rays[idx], rays_info[idx]) for idx in range(number_of_rays)]
	# 	[rays_info[idx].t_hits.sort() for idx in range(number_of_rays)]
	# 	p_total_time += time.time() - start_time
	# 	print("Python ray tracing:", time.time()- start_time)
	# 	start_time = time.time()
	# 	_rays, c_rays_info = bunny.get_c_bvh().MultiRayAllIntersects(rays_origins, rays_directions, 0, np.inf)
	# 	c_total_time +=  time.time() - start_time
	# 	print("c++ ray tracing:", time.time() - start_time)
		# start_time = time.time()
		# rays = [PyBindRay(np.array([- bbox_width * 0.5 + width_offset * i, -0.5 * bbox_height + height_offset * l_idx, bbox_depth]), np.array([0, 0, -1]), 0, np.inf, 0, 0) for i in range(number_of_rays)]
		# ray_infos = [PyBindRayInfo() for i in range(number_of_rays)]
		# [bunny.get_c_bvh().Intersect(rays[idx], ray_infos[idx]) for idx in range(number_of_rays)]
		# c_single_total_time += time.time() - start_time
		# print("c++ single int", time.time()-start_time)

		# plane_x0 = np.array([0.0, -0.5 * bbox_height + height_offset * l_idx, 0.0], dtype=np.float32)
		# plane_normal = np.array([0.0, 1.0, 0.0], dtype=np.float32)
		# #
		# start_time = time.time()
		# slice_plane = pyStructs.Plane(plane_x0, plane_normal)
		# slice_plane_info = pyStructs.PlaneIntersectionInfo()
		# bunny.get_bvh().plane_all_intersections(slice_plane, slice_plane_info)
		# p_hits = slice_plane_info.intersections
		# # print("python plane intersection", time.time() - start_time)
		# start_time = time.time()
		# slice_plane = PyBindPlane(plane_x0, plane_normal)
		# slice_plane_info = PyBindPlaneInfo()
		# bunny.get_c_bvh().PlaneAllIntersects(slice_plane, slice_plane_info)
		# c_hits = slice_plane_info.GetHits()
		# print("c++ plane intersection", time.time() - start_time)
		# # start_time = time.time()
		# # c_hits = [x for x in c_hits if x!=[]]
		# # print("c++ plane intersection removal", time.time() - start_time)
		# banana=1


	# print("c++ total ray tracing:", c_total_time)
	# print("c++ single total ray tracing:", c_single_total_time)
	# print("python total ray tracing:", p_total_time)
	rays_origins = [np.array([- bbox_width * 0.5 + width_offset * idx, -0.5 * bbox_height + height_offset * l_idx, bbox_depth]) for idx in
						range(number_of_rays) for l_idx in range(number_of_layers)]
	rays_directions = [np.array([0, 0, -1]) for idx in range(number_of_rays * number_of_layers)]
	start_time = time.time()
	_rays, c_rays_info = bunny.get_c_bvh().MultiRayAllIntersects(rays_origins, rays_directions, 0, np.inf)
	c_total_time += time.time() - start_time
	print("c++ super mega ray tracing:", time.time() - start_time)



	# l = 5
	# offset = 2.0 * l / number_of_rays
	# h_offset = 2.0 * l / number_of_layers
	# # print("generating primitives", time.time() - start_time)
	# triangles, primitives = build_cube(l)
	# flat_list = [item for sublist in primitives for item in sublist]
	# start_time = time.time()
	# cbvh = PyBindBVH(flat_list, PyBindBVH.EqualCounts, 255)
	# print("(c++ measured from python) BVH construction", time.time() - start_time)
	# start_time = time.time()
	# pbvh = pyBVH.BVH(triangles, 'EqualCounts')
	# print("Python BVH construction", time.time() - start_time)
	#
	# for l_idx in range(number_of_layers):
	# 	plane_x0 = np.array([0.0, -l + h_offset * l_idx, 0.0], dtype=np.float32)
	# 	plane_normal = np.array([0.0, 1.0, 0.0], dtype=np.float32)
	# 	start_time = time.time()
	# 	slice_plane = pyStructs.Plane(plane_x0, plane_normal)
	# 	slice_plane_info = pyStructs.PlaneIntersectionInfo()
	# 	pbvh.plane_all_intersections(slice_plane, slice_plane_info)
	# 	p_hits = slice_plane_info.intersections
	# 	print("python plane intersection", time.time() - start_time)
	# 	start_time = time.time()
	# 	slice_plane = PyBindPlane(plane_x0, plane_normal)
	# 	slice_plane_info = PyBindPlaneInfo()
	# 	cbvh.PlaneAllIntersects(slice_plane, slice_plane_info)
	# 	c_hits = slice_plane_info.GetHits()
	# 	# print(c_hits)
	# 	c_hits = [x for x in c_hits if x!=[]]
	# 	print("c++ plane intersection", time.time() - start_time)
	# 	banana = 1
	# # #
	# #
	# #
	# #
	# start_time = time.time()
	# rays = [st.Ray(np.array([-l + i * offset, 0, l + 1]), np.array([0, 0, -1]), 0, 1000, 0, 0) for i in range(number_of_rays)]
	# ray_infos = [st.RayIntersectionInfo() for i in range(number_of_rays)]
	# [pbvh.intersect(rays[idx], ray_infos[idx]) for idx in range(number_of_rays)]
	# print("Python intersection time", time.time() - start_time)
	# #
	# # start_time = time.time()
	# # rays = [PyBindRay(np.array([-l + i * offset, 0, l + 1]), np.array([0, 0, -1]), 0, 1000, 0, 0) for i in range(number_of_rays)]
	# # ray_infos = [PyBindRayInfo() for i in range(number_of_rays)]
	# # [cbvh.Intersect(rays[idx], ray_infos[idx]) for idx in range(number_of_rays)]
	# # print("c++ intersection time", time.time() - start_time)
	#
	# start_time = time.time()
	# origins = [np.array([-l + i * offset, 0, l + 1]) for i in range(number_of_rays)]
	# directions = [np.array([0, 0, -1]) for i in range(number_of_rays)]
	# # print("c++ multiray creation time", time.time() - start_time)
	# # start_time = time.time()
	# rays, infos = cbvh.MultiRayAllIntersects(origins, directions, 0, 1000)
	# print("c++ multi intersection time", time.time() - start_time)
	# # for idx in range(number_of_rays):
	# # 	print(infos[idx].GetHits())
	# # print([infos[idx].GetHits() for idx in range(len(infos))])
