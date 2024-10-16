import time
import rasterio
import numpy as np
import os
from geometry import *
from save_glb import export_to_glb_from_data

def sample_raster_color(dataset, lat, lon):
    # Handle wrapping of longitude
    if lon < -180:
        lon += 360
    elif lon > 180:
        lon -= 360

    # Transform the (lon, lat) to the dataset's row and col
    try:
        # Note: rasterio uses (lon, lat) ordering
        row, col = dataset.index(lon, lat)
        # Read the RGB value at that row and col
        # dataset.read() returns arrays with shape (band, rows, cols)
        rgb = dataset.read([1, 2, 3], window=((row, row+1), (col, col+1))).flatten()
        # Convert to integers and ensure values are within [0, 255]
        rgb = tuple(int(c) for c in rgb)
        return rgb
    except IndexError:
        # If the point is outside the raster bounds
        return (0, 0, 0)  # Return black or some default color

def process_chunk(chunk):
    x_chunk, y_chunk, z_chunk = [], [], []
    indices_chunk = []
    face_colors_rgb_chunk = []
    vertex_count_chunk = 0

    # Open the raster dataset within each worker
    with rasterio.open('NE2_HR_LC_SR_W_DR/NE2_HR_LC_SR_W_DR.tif') as dataset:
        for face_vertices in chunk:
            # Triangulate the face
            triangles = triangulate_face(face_vertices)

            # Compute centroid for color sampling
            centroid_cartesian = np.mean(face_vertices, axis=0)
            centroid_cartesian /= np.linalg.norm(centroid_cartesian)
            lat_c, lon_c = cartesian_to_spherical(*centroid_cartesian)

            # Sample color
            color_rgb = sample_raster_color(dataset, lat_c, lon_c)
            color_rgb_float = [c / 255.0 for c in color_rgb]

            for triangle in triangles:
                face_indices = []
                for vertex in triangle:
                    x_chunk.append(vertex[0])
                    y_chunk.append(vertex[1])
                    z_chunk.append(vertex[2])
                    face_indices.append(vertex_count_chunk)
                    vertex_count_chunk += 1

                indices_chunk.extend(face_indices)
                face_colors_rgb_chunk.extend(color_rgb_float * 3)  # Each vertex gets the face color

    return x_chunk, y_chunk, z_chunk, indices_chunk, face_colors_rgb_chunk

def generate_final_sphere(dual_faces, file_name):
    start_time = time.time()
    print("Starting plot generation...")

    # Open temporary files
    vertex_file = open('temp_vertices.bin', 'wb')
    index_file = open('temp_indices.bin', 'wb')
    color_file = open('temp_colors.bin', 'wb')

    total_vertices = 0
    total_indices = 0

    # Open the raster dataset once
    with rasterio.open('NE2_HR_LC_SR_W_DR/NE2_HR_LC_SR_W_DR.tif') as dataset:
        for face_vertices in dual_faces:
            # Triangulate the face
            triangles = triangulate_face(face_vertices)

            # Compute centroid for color sampling
            centroid_cartesian = np.mean(face_vertices, axis=0)
            centroid_cartesian /= np.linalg.norm(centroid_cartesian)
            lat_c, lon_c = cartesian_to_spherical(*centroid_cartesian)

            # Sample color
            color_rgb = sample_raster_color(dataset, lat_c, lon_c)
            color_rgb_float = [c / 255.0 for c in color_rgb]

            for triangle in triangles:
                # Prepare vertex data
                triangle_vertices = np.array(triangle, dtype=np.float32)
                vertex_file.write(triangle_vertices.tobytes())

                # Prepare index data
                triangle_indices = np.arange(total_vertices, total_vertices + 3, dtype=np.uint32)
                index_file.write(triangle_indices.tobytes())

                # Prepare color data
                face_colors = np.tile(color_rgb_float, (3, 1)).astype(np.float32)
                color_file.write(face_colors.tobytes())

                total_vertices += 3
                total_indices += 3

    # Close temporary files
    vertex_file.close()
    index_file.close()
    color_file.close()

    # Now, read the data from the temporary files and assemble the GLB
    with open('temp_vertices.bin', 'rb') as vertex_file, \
         open('temp_indices.bin', 'rb') as index_file, \
         open('temp_colors.bin', 'rb') as color_file:

        vertex_data = vertex_file.read()
        index_data = index_file.read()
        color_data = color_file.read()

        # Prepare data for export_to_glb
        num_vertices = total_vertices
        num_indices = total_indices

        # Proceed to create the GLB file
        export_to_glb_from_data(file_name, vertex_data, index_data, color_data, num_vertices, num_indices)

    # Remove temporary files
    os.remove('temp_vertices.bin')
    os.remove('temp_indices.bin')
    os.remove('temp_colors.bin')

    # Rotate the sphere
    print("Now rotating...")
    rotate_sphere(file_name)
    print("Finished rotating.")

    print(f"Plot generation completed. Time taken: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    begin_time = time.time()
    frequency = 10  # Adjust this value for more hexagons (higher frequency)

    vertices, faces = create_geodesic_sphere(frequency)
    dual_faces, face_types = compute_dual(vertices, faces)
    count_hexagons_pentagons(face_types)
    generate_final_sphere(dual_faces, f"geodesic_sphere_{frequency}.glb")

    print(f"Total elapsed time: {time.time() - begin_time:.2f}s")