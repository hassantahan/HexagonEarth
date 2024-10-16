import time
import trimesh
import numpy as np
from collections import defaultdict
from datetime import datetime

def count_hexagons_pentagons(face_types):
    hexagon_count = sum(1 for face_type in face_types if face_type == 6)
    pentagon_count = sum(1 for face_type in face_types if face_type == 5)
    
    print(f"Number of Hexagons: {hexagon_count}")
    print(f"Number of Pentagons: {pentagon_count}")
    
    return hexagon_count, pentagon_count

def cartesian_to_spherical(x, y, z):
    # Compute the longitude
    lon = np.arctan2(y, x) * (180 / np.pi)
    # Compute the hypotenuse on the XY plane
    hyp = np.sqrt(x**2 + y**2)
    # Compute the latitude
    lat = np.arctan2(z, hyp) * (180 / np.pi)
    return lat, lon

def generate_icosahedron():
    start_time = time.time()
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [Geometry] Generating icosahedron vertices...")

    # Golden ratio
    phi = (1 + np.sqrt(5)) / 2
    # Create the 12 vertices of an icosahedron
    vertices = [
        [-1,  phi,  0],
        [ 1,  phi,  0],
        [-1, -phi,  0],
        [ 1, -phi,  0],
        [ 0, -1,  phi],
        [ 0,  1,  phi],
        [ 0, -1, -phi],
        [ 0,  1, -phi],
        [ phi,  0, -1],
        [ phi,  0,  1],
        [-phi,  0, -1],
        [-phi,  0,  1],
    ]
    # Convert to NumPy arrays and normalize
    vertices = [np.array(v, dtype=float) for v in vertices]
    for i, v in enumerate(vertices):
        vertices[i] = v / np.linalg.norm(v)

    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [Geometry] Icosahedron generated. Time taken: {time.time() - start_time:.2f} seconds.")
    return vertices

def subdivide(vertices, faces):
    start_time = time.time()
    print("Subdividing faces...")
    new_faces = []
    midpoints = {}
    def midpoint(i1, i2):
        key = tuple(sorted((i1, i2)))
        if key not in midpoints:
            v1 = vertices[i1]
            v2 = vertices[i2]
            mid = (v1 + v2) / 2.0
            mid /= np.linalg.norm(mid)
            midpoints[key] = len(vertices)
            vertices.append(mid)
        return midpoints[key]
        
    for tri in faces:
        v1, v2, v3 = tri
        a = midpoint(v1, v2)
        b = midpoint(v2, v3)
        c = midpoint(v3, v1)
        new_faces.extend([
            [v1, a, c],
            [v2, b, a],
            [v3, c, b],
            [a, b, c],
        ])

    print(f"Subdivision complete. {len(new_faces)} faces created. Time taken: {time.time() - start_time:.2f} seconds.")
    return new_faces

def create_geodesic_sphere(frequency):
    start_time = time.time()
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [Geometry] Creating geodesic sphere with frequency: {frequency}")

    vertices = generate_icosahedron()  # List of NumPy arrays

    # Faces of an icosahedron
    faces = [
        [0, 11, 5], [0, 5, 1], [0,1,7], [0,7,10], [0,10,11],
        [1,5,9], [5,11,4], [11,10,2], [10,7,6], [7,1,8],
        [3,9,4], [3,4,2], [3,2,6], [3,6,8], [3,8,9],
        [4,9,5], [2,4,11], [6,2,10], [8,6,7], [9,8,1]
    ]
    # Subdivide faces
    for i in range(frequency):
        print(f"Subdivision step {i + 1}/{frequency}...")
        faces = subdivide(vertices, faces)

    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [Geometry] Geodesic sphere created. Total time: {time.time() - start_time:.2f} seconds.")
    return vertices, faces

def compute_dual(vertices, faces):
    start_time = time.time()
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [Geometry] Computing dual polyhedron...")

    # Build a mapping from each vertex to the adjacent faces
    vertex_faces = defaultdict(list)
    for face_idx, face in enumerate(faces):
        for v_idx in face:
            vertex_faces[v_idx].append(face_idx)
    # Build the dual faces
    dual_faces = []
    face_types = []
    for v_idx in range(len(vertices)):
        adjacent_faces = vertex_faces[v_idx]
        # For each vertex, get the centroids of its neighboring faces
        face_vertices = []
        for f_idx in adjacent_faces:
            face = faces[f_idx]
            centroid = np.mean([vertices[i] for i in face], axis=0)
            centroid /= np.linalg.norm(centroid)
            face_vertices.append(centroid)
        # Order the face vertices to form a proper polygon
        face_vertices = order_polygon(face_vertices, vertices[v_idx])
        dual_faces.append(face_vertices)
        face_types.append(len(face_vertices))

    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [Geometry] Dual polyhedron computed. Time taken: {time.time() - start_time:.2f} seconds.")
    return dual_faces, face_types

def order_polygon(vertices, center):
    #start_time = time.time()
    #print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [Geometry] Ordering the polygons...")

    # Compute the normal vector at the center
    normal = center / np.linalg.norm(center)
    # Choose two orthogonal reference directions in the plane perpendicular to the normal
    if np.allclose(normal, [0, 0, 1]) or np.allclose(normal, [0, 0, -1]):
        ref_x = np.array([1, 0, 0])
    else:
        ref_x = np.cross([0, 0, 1], normal)
        ref_x /= np.linalg.norm(ref_x)
    ref_y = np.cross(normal, ref_x)
    # Project vertices onto plane perpendicular to normal and compute angle
    angles = []
    for v in vertices:
        vec = v - center
        x = np.dot(vec, ref_x)
        y = np.dot(vec, ref_y)
        angle = np.arctan2(y, x)
        angles.append(angle)
    # Sort vertices based on angle
    vertices = [v for _, v in sorted(zip(angles, vertices))]

    #print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [Geometry] Polygons ordered. Time taken: {time.time() - start_time:.2f} seconds.")
    return vertices

def triangulate_face(face_vertices):
    #start_time = time.time()
    #print("Face triangulation...")

    # Triangulate a polygon face (hexagon/pentagon) into triangles.
    centroid = np.mean(face_vertices, axis=0)
    triangles = []
    n = len(face_vertices)
    
    for i in range(n):
        triangles.append([face_vertices[i], face_vertices[(i + 1) % n], centroid])
    
    #print(f"Faces have been triangulated. Time taken: {time.time() - start_time:.2f} seconds.")
    return triangles

def rotate_sphere(file_name):
    # Load the GLB file
    mesh = trimesh.load(file_name)

    # Define a rotation matrix for 90 degrees around the X-axis
    rotation_matrix = trimesh.transformations.rotation_matrix(
        angle=np.radians(-90),  # 90-degree rotation
        direction=[1, 0, 0],   # X-axis rotation
        point=mesh.centroid    # Rotate around the center of the model
    )

    # Apply the transformation to the mesh
    mesh.apply_transform(rotation_matrix)

    # Export the rotated model
    mesh.export(file_name)