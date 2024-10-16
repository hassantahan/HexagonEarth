# Hexagon # **Hexagon Earth 3D Model Generator**

This project generates a 3D Earth model using a geodesic sphere made up of hexagons and pentagons. The vertices and faces of the sphere are computed and then processed to assign colors sampled from a high-resolution raster image of the Earth’s surface. The final output is a 3D model in **GLB** format with face colors preserved.

The code is optimized for memory efficiency and can handle large models by using a chunked approach to process vertices and colors incrementally, reducing the risk of memory overflows.

## **Features**
- Generates 3D models using geodesic spheres with varying frequencies (detail levels).
- Assigns colors to each face of the sphere by sampling from a raster image of the Earth.
- Outputs the 3D model in **GLB** format, which can be viewed in 3D model viewers like [Blender](https://www.blender.org/), [three.js](https://threejs.org/), or [glTF Viewer](https://gltf-viewer.donmccurdy.com/).
- Optimized for handling large datasets by processing in chunks to minimize memory usage.

## **Project Structure**

```
.
├── geometry.py              # Geodesic sphere generation and face triangulation logic
├── main.py                  # Main script for generating the sphere and saving it as GLB
├── save_glb.py              # Functions for exporting 3D model to GLB format
├── README.md                # Project README
└── NE2_HR_LC_SR_W_DR/
  ├── NE2_HR_LC_SR_W_DR.tif 			# Raster image used for sampling Earth colors (taken from Natural Earth Data; see below)
  ├── NE2_HR_LC_SR_W_DR.tfw
  ├── NE2_HR_LC_SR_W_DR.VERSION.txt
  ├── NE2_HR_LC_SR_W_DR.README.html
  └── NE2_HR_LC_SR_W_DR.prj
```

## **Setup**

### **Requirements**
Make sure you have the following dependencies installed before running the code:

- Python 3.8+
- `numpy`
- `rasterio`
- `trimesh`
- `pygltflib`

You can install the required packages using `pip`:

```bash
pip install numpy rasterio trimesh pygltflib
```

### **Downloading Earth Raster Image**
This project requires a high-resolution raster image of the Earth, **`NE2_HR_LC_SR_W_DR.tif`**. You can download this file from [Natural Earth](https://www.naturalearthdata.com/downloads/10m-raster-data/10m-natural-earth-2/). Place the downloaded file inside the main directory.

## **Usage**

1. Clone the repository:

   ```bash
   git clone https://github.com/hassantahan/HexagonEarth
   ```

2. Adjust the frequency of the geodesic sphere in the `main.py` file:

   ```python
   frequency = 5  # Change this value to increase or decrease sphere detail
   ```

3. Run the main script to generate the 3D model:

   ```bash
   python main.py
   ```

   This will generate a GLB file with the name `geodesic_sphere_<frequency>.glb`, which can be viewed in a 3D viewer.

### **Memory Optimization**

I am currently working on optimizing the memory usage of this script. It uses A LOT at higher frequencies.

At the moment, I am working out removing duplicate vertices where colours match. I am also looking into moving from a GLB file to something else that allows continuous writing as for now I had to resort to storing the data into binary files to generate a 10-frequency globe.

## **File Descriptions**

### **`geometry.py`**
Contains the core functions for generating a geodesic sphere, including:
- **`create_geodesic_sphere(frequency)`**: Generates the vertices and faces of the sphere with a specified level of detail (frequency).
- **`triangulate_face()`**: Triangulates hexagon and pentagon faces into triangles for GLB export.

### **`main.py`**
The main entry point for the project:
- Generates the geodesic sphere.
- Samples colors from the raster image.
- Exports the 3D model into GLB format.

### **`save_glb.py`**
Handles exporting the sphere to GLB format:
- **`export_to_glb()`**: Converts the vertices, indices, and face colors into the GLB format.

## **Customization**

- **Geodesic Sphere Detail**: Adjust the `frequency` parameter in `main.py` to control the level of detail for the geodesic sphere. Higher values generate more faces but require more memory and processing power.
  
- **Face Color Sampling**: The color of each face is sampled from a raster image of the Earth. You can customize this by using a different raster image in the `data/` directory and modifying the `sample_raster_color()` function.

## **Future Improvements**
- Memory optimization (see above)
- Add support for different 3D file formats.
- Implement additional optimizations for faster generation of large models.
- Add texture support for higher realism.

## **Contributing**

Contributions are welcome! If you'd like to improve this project, please submit a pull request or open an issue for any bugs or feature requests.
