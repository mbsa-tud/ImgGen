# ImageGen Project

## Overview

The **ImageGen** project is designed to automate image generation and scene rendering using Blender. The project uses BlenderProc for setting up and rendering 3D scenes, randomizing various scene parameters, and checking for safety constraints. It also saves metadata, such as safety violations and distances, for each generated image. This project is ideal for creating annotated datasets for tasks like computer vision, robotics, or synthetic data generation.

## Key Features

- **Automatic Scene Setup**: Loads and assigns 3D models (e.g., table, workpiece, worker, and panda manipulator) from a `.blend` file.
- **Parameter Randomization**: Randomizes the position, size, and orientation of objects in the scene for variation.
- **Collision and Safety Checking**: Includes logic to check for collisions between specific objects and enforce safety zones.
- **Rendering and Annotation**: Renders images and segmentation maps and logs metadata in CSV format for easy analysis.
- **Documentation Generation**: Uses `pdoc` or `Sphinx` to generate documentation from inline docstrings.

## Directory Structure

```plaintext
ImageGen/
│
├── temp.py                    # Main script for rendering pipeline
├── config.json                # Configuration file with rendering and scene parameters
├── README.md                  # Project documentation
├── docs/                      # Folder for generated documentation
│
├── modules/
│   ├── __init__.py
│   ├── scene_setup.py         # Functions for loading and assigning scene objects
│   ├── randomization.py       # Functions to randomize object parameters
│   ├── safety.py              # Functions for collision and safety checks
│   ├── render.py              # Functions for rendering and saving images
│   └── utils.py               # Utility functions for logging and cleanup
│
└── venv/                      # Python virtual environment (optional)
```

## Setup

### Prerequisites

- **Blender**: Ensure Blender is installed, and you can use Blender’s `bpy` module.
- **Python 3.8+**: The project uses Python to interact with Blender and render scenes.
- **BlenderProc**: Install BlenderProc, a procedural Blender scripting tool, using the following command:

  ```bash
  pip install blenderproc
  ```

### Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/ImageGen.git
   cd ImageGen
   ```

2. **Set Up Virtual Environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Required Packages**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Project**: Update `config.json` with your desired rendering parameters, file paths, and randomization ranges.

## Usage

To run the main rendering pipeline, execute the following command:

```bash
python temp.py
```

### Configuration

The `config.json` file allows you to control various aspects of the rendering pipeline, including:

- **Scene Parameters**: Adjusts the scene file path, camera settings, light properties, object categories, and randomization ranges.
- **Rendering Parameters**: Sets output directory and number of images to render.
- **Safety Zone Parameters**: Specifies minimum distances between objects to ensure compliance with safety rules.

### Documentation Generation

You can generate HTML documentation from docstrings using `pdoc` or `Sphinx`.

#### Using pdoc

To generate and view documentation in HTML format, run:

```bash
pdoc temp.py -o docs
```

This will save the documentation in the `docs` folder.

#### Using Sphinx

To generate Sphinx documentation:

1. Initialize Sphinx (if not already initialized):

   ```bash
   sphinx-quickstart
   ```

2. Configure `conf.py` to use `autodoc` and add your project’s path.

3. Generate HTML documentation:

   ```bash
   sphinx-apidoc -o source/ .
   sphinx-build -b html source/ docs/
   ```

Open `docs/index.html` in your browser to view the generated documentation.

## Code Overview

### Main Modules and Functions

- **`load_config`**: Loads settings from `config.json` to control the pipeline.
- **`load_scene_from_blend`**: Loads objects from a Blender `.blend` file and categorizes them for easy access.
- **`randomize_*` functions**: Randomizes object properties (e.g., position, rotation) to introduce variability across renders.
- **`collision_check_*` functions**: Checks for collisions and ensures compliance with safety zones by adjusting object positions.
- **`render_scene`**: Renders the scene and saves both images and segmentation maps.
- **`log_to_csv`**: Logs metadata (e.g., violation flags, distances) to a CSV file for each image.

### Main Script: `temp.py`

The main script initializes the rendering environment, loads configurations, sets up the scene, performs randomization, checks for safety violations, renders images, and logs metadata. This script iterates through the specified number of images to generate a diverse set of renders.

## Example Workflow

1. **Set up** the `config.json` file with your preferred parameters.
2. **Run** the `temp.py` script to generate images in bulk with varied parameters.
3. **View** generated images and analyze metadata in `rendered_data.csv`.
4. **Generate documentation** to understand the codebase, if needed.

## Contributing

If you'd like to contribute, please fork the repository and make changes as you'd like. Pull requests are warmly welcome.

1. Fork this repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
