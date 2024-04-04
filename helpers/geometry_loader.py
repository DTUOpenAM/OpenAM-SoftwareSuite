from PySide2.QtCore import QFileInfo, QTime
from PySide2.QtGui import QVector3D
import numpy as np
import struct


# load stl file detects if the file is a text file or binary file
def load_geometry(file_name, swap_yz=False):
    file_extension = QFileInfo(file_name).suffix()
    if file_extension.lower() == 'obj':
        return load_obj(file_name, swap_yz)
    elif file_extension.lower() == 'stl':
        return load_stl(file_name, swap_yz)
    
    
def load_stl(filename, swap_yz=False):
    # read start of file to determine if its a binay stl file or a ascii stl file
    if not filename:
        return False
    fp = open(filename, 'rb')
    try:
        header = fp.read(80 + 20).decode('ASCII')  # read 80 bytes for heade plus 20 bytes to avoid SolidWorks Binary files
        stl_type = header[0:5]
    except UnicodeDecodeError:
        stl_type = 'binary'
    fp.close()
    if stl_type == 'solid':
        is_loaded, vertices_list, normals_list, bbox_min, bbox_max = load_text_stl(filename, swap_yz)
        if not is_loaded:
            return load_binary_stl(filename, swap_yz)
        else:
            return is_loaded, vertices_list, normals_list, bbox_min, bbox_max
    else:
        return load_binary_stl(filename, swap_yz)


# read text stl match keywords to grab the points to build the model
def load_text_stl(filename, swap_yz=False, test=True):
    number_of_triangles = 0
    normals_list = []
    vertices_list = []
    is_bbox_defined = False
    bbox_min = None
    bbox_max = None
    stl_file = open(filename, 'r')
    # time = QTime()
    # time.start()
    # t = time.elapsed()

    try:
        for line in stl_file:
            words = line.split()
            if len(words) > 0:
                if words[0] == 'facet':
                    number_of_triangles += 1
                    v = [float(words[2]), float(words[3]), float(words[4])]
                    if swap_yz:
                        v = [-v[0], v[2], v[1]]
                    normals_list.append(v)
                    normals_list.append(v)
                    normals_list.append(v)
                if words[0] == 'vertex':
                    v = [float(words[1]), float(words[2]), float(words[3])]
                    if swap_yz:
                        v = [-v[0], v[2], v[1]]
                    vertices_list.append(v)
                    if is_bbox_defined:
                        bbox_min = np.minimum(bbox_min, v)
                        bbox_max = np.maximum(bbox_max, v)
                    else:
                        bbox_max = v
                        bbox_min = v
                        is_bbox_defined = True
    except Exception as e:
        stl_file.close()
        return False, vertices_list, normals_list, bbox_min, bbox_max
    # print("Read file", time.elapsed() - t)
    # t = time.elapsed()
    stl_file.close()
    # bbox recentering around origin
    bbox_min = QVector3D(bbox_min[0], bbox_min[1], bbox_min[2])
    bbox_max = QVector3D(bbox_max[0], bbox_max[1], bbox_max[2])
    bbox_center = 0.5 * (bbox_min + bbox_max)
    bbox_center_array = np.array(bbox_center.toTuple())
    vertices_list = [vertices_list[idx] - bbox_center_array for idx in range(len(vertices_list))]
    bbox_min = bbox_min - bbox_center
    bbox_max = bbox_max - bbox_center
    vertices_list = np.array(vertices_list, dtype=np.float32).ravel()
    normals_list = np.array(normals_list, dtype=np.float32).ravel()
    # print("Read faces", time.elapsed() - t)
    return True, vertices_list, normals_list, bbox_min, bbox_max


def load_binary_stl(filename, swap_yz=False):
    normals_list = []
    vertices_list = []
    is_bbox_defined = False
    bbox_min = None
    bbox_max = None
    fp = open(filename, 'rb')
    # time = QTime()
    # time.start()
    # t = time.elapsed()
    header = fp.read(80)
    # read 4 bytes describing the number of triangles, and convert them to integer
    number_of_triangles = struct.unpack('I', fp.read(4))[0]
    for idx in range(number_of_triangles):
        try:
            normal_bytes = fp.read(12)
            if len(normal_bytes) == 12:
                normal = struct.unpack('f', normal_bytes[0:4])[0], struct.unpack('f', normal_bytes[4:8])[0], \
                         struct.unpack('f', normal_bytes[8:12])[0]
                if swap_yz:
                    normal = [-normal[0], normal[2], normal[1]]
                normals_list.append(normal)
                normals_list.append(normal)
                normals_list.append(normal)
            v0_bytes = fp.read(12)
            if len(v0_bytes) == 12:
                v0 = struct.unpack('f', v0_bytes[0:4])[0], struct.unpack('f', v0_bytes[4:8])[0], \
                     struct.unpack('f', v0_bytes[8:12])[0]
                if swap_yz:
                    v0 = [-v0[0], v0[2], v0[1]]
                vertices_list.append(v0)
                if is_bbox_defined:
                    bbox_min = np.minimum(bbox_min, v0)
                    bbox_max = np.maximum(bbox_max, v0)
                else:
                    bbox_max = v0
                    bbox_min = v0
                    is_bbox_defined = True
            v1_bytes = fp.read(12)
            if len(v1_bytes) == 12:
                v1 = struct.unpack('f', v1_bytes[0:4])[0], struct.unpack('f', v1_bytes[4:8])[0], \
                     struct.unpack('f', v1_bytes[8:12])[0]
                if swap_yz:
                    v1 = [-v1[0], v1[2], v1[1]]
                vertices_list.append(v1)
                if is_bbox_defined:
                    bbox_min = np.minimum(bbox_min, v1)
                    bbox_max = np.maximum(bbox_max, v1)
                else:
                    bbox_max = v1
                    bbox_min = v1
                    is_bbox_defined = True
            v2_bytes = fp.read(12)
            if len(v2_bytes) == 12:
                v2 = struct.unpack('f', v2_bytes[0:4])[0], struct.unpack('f', v2_bytes[4:8])[0], \
                     struct.unpack('f', v2_bytes[8:12])[0]
                v2 = [-v2[0], v2[2], v2[1]]
                vertices_list.append(v2)
                if is_bbox_defined:
                    bbox_min = np.minimum(bbox_min, v2)
                    bbox_max = np.maximum(bbox_max, v2)
                else:
                    bbox_max = v2
                    bbox_min = v2
                    is_bbox_defined = True
            attribute_bytes = fp.read(2)
            if len(attribute_bytes) == 0:
                break
        except EOFError:
            break
        except Exception as e:
            return False, vertices_list, normals_list, bbox_min, bbox_max
    # print("Read file", time.elapsed() - t)
    # t = time.elapsed()
    fp.close()
    ######## bbox recentering around origin
    bbox_min = QVector3D(bbox_min[0], bbox_min[1], bbox_min[2])
    bbox_max = QVector3D(bbox_max[0], bbox_max[1], bbox_max[2])
    bbox_center = 0.5 * (bbox_min + bbox_max)
    bbox_center_array = np.array(bbox_center.toTuple())
    vertices_list = [vertices_list[idx] - bbox_center_array for idx in range(len(vertices_list))]
    bbox_min = bbox_min - bbox_center
    bbox_max = bbox_max - bbox_center
    vertices_list = np.array(vertices_list, dtype=np.float32).ravel()
    normals_list = np.array(normals_list, dtype=np.float32).ravel()
    # print("Read faces", time.elapsed() - t)
    return True, vertices_list, normals_list, bbox_min, bbox_max


def load_obj(filename, swap_yz=False):
    """Loads a Wavefront OBJ file. """
    number_of_triangles = 0
    normals_list = []
    vertices_list = []
    is_bbox_defined = False
    bbox_min = None
    bbox_max = None
    tmp_vertices = []
    tmp_normals = []
    tmp_faces = []
    obj_file = open(filename, 'r')
    # time = QTime()
    # time.start()
    # t = time.elapsed()

    def read_obj_line(line):
        nonlocal is_bbox_defined, bbox_min, bbox_max, number_of_triangles
        if line.startswith('#'):
            return
        values = line.split()
        if not values:
            return
        if values[0] == 'v':
            if swap_yz:
                v = [-float(values[1]), float(values[3]), float(values[2])]
            else:
                v = [float(values[1]), float(values[2]), float(values[3])]
            tmp_vertices.append(v)
            if is_bbox_defined:
                bbox_min = np.minimum(bbox_min, v)
                bbox_max = np.maximum(bbox_max, v)
            else:
                bbox_max = v
                bbox_min = v
                is_bbox_defined = True
        elif values[0] == 'vn':
            v = [float(values[1]), float(values[2]), float(values[3])]
            if swap_yz:
                v = [-v[0], v[2], v[1]]
            tmp_normals.append(v)
        elif values[0] == 'f':
            number_of_triangles += 1
            face = []
            norms = []
            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                if len(w) >= 3 and len(w[2]) > 0:
                    norms.append(int(w[2]))
                else:
                    norms.append(0)
            tmp_faces.append((face, norms))
    [read_obj_line(line) for line in obj_file]
    ###### bbox recentering around origin
    # print("Read file", time.elapsed() - t)
    # t = time.elapsed()
    bbox_min = QVector3D(bbox_min[0], bbox_min[1], bbox_min[2])
    bbox_max = QVector3D(bbox_max[0], bbox_max[1], bbox_max[2])
    bbox_center = 0.5 * (bbox_min + bbox_max)
    bbox_min = bbox_min - bbox_center
    bbox_max = bbox_max - bbox_center
    ###### read faces

    def read_face(face):
        nonlocal normals_list, vertices_list, tmp_normals, tmp_vertices, bbox_center
        vertices_idx, normals_idx = face
        for i in range(len(vertices_idx)):
            if normals_idx[i] > 0:
                normals_list.append(tmp_normals[normals_idx[i]-1][0])
                normals_list.append(tmp_normals[normals_idx[i]-1][1])
                normals_list.append(tmp_normals[normals_idx[i]-1][2])
            vertices_list.append(tmp_vertices[vertices_idx[i]-1][0] - bbox_center.x())
            vertices_list.append(tmp_vertices[vertices_idx[i]-1][1] - bbox_center.y())
            vertices_list.append(tmp_vertices[vertices_idx[i]-1][2] - bbox_center.z())
    [read_face(face) for face in tmp_faces]

    vertices_list = np.array(vertices_list, dtype=np.float32).ravel()
    normals_list = np.array(normals_list, dtype=np.float32).ravel()
    obj_file.close()
    # print("Read faces", time.elapsed() - t)
    return True, vertices_list, normals_list, bbox_min, bbox_max
