from pygltflib import GLTF2, Scene, Mesh, Node, Buffer, BufferView, Accessor, Asset, Primitive
import numpy as np

# glTF constants
ARRAY_BUFFER = 34962
ELEMENT_ARRAY_BUFFER = 34963
FLOAT = 5126
UNSIGNED_INT = 5125
VEC3 = "VEC3"
SCALAR = "SCALAR"

def export_to_glb_from_data(filename, vertex_data, index_data, color_data, num_vertices, num_indices):
    # Ensure data types are bytes
    if not isinstance(vertex_data, bytes):
        print("Error: vertex_data is not bytes.")
        return
    if not isinstance(index_data, bytes):
        print("Error: index_data is not bytes.")
        return
    if not isinstance(color_data, bytes):
        print("Error: color_data is not bytes.")
        return

    # Verify buffer lengths
    expected_vertex_data_length = num_vertices * 3 * 4  # 3 floats per vertex
    expected_index_data_length = num_indices * 4        # 1 uint32 per index
    expected_color_data_length = num_vertices * 3 * 4   # 3 floats per color

    if len(vertex_data) != expected_vertex_data_length:
        print(f"Error: vertex_data length {len(vertex_data)} does not match expected length {expected_vertex_data_length}.")
        return
    if len(index_data) != expected_index_data_length:
        print(f"Error: index_data length {len(index_data)} does not match expected length {expected_index_data_length}.")
        return
    if len(color_data) != expected_color_data_length:
        print(f"Error: color_data length {len(color_data)} does not match expected length {expected_color_data_length}.")
        return


    # Combine buffers
    buffer_data = vertex_data + index_data + color_data

    # Create buffer object
    buffer = Buffer(uri=None, byteLength=len(buffer_data))
    gltf = GLTF2()
    gltf.buffers.append(buffer)
    gltf.set_binary_blob(buffer_data)

    # Create buffer views
    vertex_buffer_view = BufferView(buffer=0, byteOffset=0, byteLength=len(vertex_data), target=ARRAY_BUFFER)
    index_buffer_view = BufferView(buffer=0, byteOffset=len(vertex_data), byteLength=len(index_data), target=ELEMENT_ARRAY_BUFFER)
    color_buffer_view = BufferView(buffer=0, byteOffset=len(vertex_data) + len(index_data), byteLength=len(color_data), target=ARRAY_BUFFER)

    gltf.bufferViews.extend([vertex_buffer_view, index_buffer_view, color_buffer_view])

    # Create accessors
    vertex_accessor = Accessor(bufferView=0, byteOffset=0, componentType=FLOAT, count=num_vertices, type=VEC3)
    index_accessor = Accessor(bufferView=1, byteOffset=0, componentType=UNSIGNED_INT, count=num_indices, type=SCALAR)
    color_accessor = Accessor(bufferView=2, byteOffset=0, componentType=FLOAT, count=num_vertices, type=VEC3)

    gltf.accessors.extend([vertex_accessor, index_accessor, color_accessor])

    # Create mesh
    primitive = Primitive(attributes={"POSITION": 0, "COLOR_0": 2}, indices=1)
    mesh = Mesh(primitives=[primitive])
    gltf.meshes.append(mesh)

    # Create node
    node = Node(mesh=0)
    gltf.nodes.append(node)

    # Create scene
    scene = Scene(nodes=[0])
    gltf.scenes.append(scene)
    gltf.scene = 0

    gltf.asset = Asset(version="2.0")

    # Save GLB file
    gltf.save(filename)