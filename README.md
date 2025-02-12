![](https://www.beschaeftigte.uni-stuttgart.de/uni-services/oeffentlichkeitsarbeit/corporate-design/cd-dateien/01_Logo/png/unistuttgart_logo_deutsch_cmyk-01.png)

<table>
  <tr>
    <td><img src="https://www.beschaeftigte.uni-stuttgart.de/uni-services/oeffentlichkeitsarbeit/corporate-design/cd-dateien/01_Logo/png/unistuttgart_logo_deutsch_cmyk-01.png" alt="Logo 1" width="150"></td>
    <td><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Bundesanstalt_f%C3%BCr_Arbeitsschutz_und_Arbeitsmedizin_Logo.svg/1024px-Bundesanstalt_f%C3%BCr_Arbeitsschutz_und_Arbeitsmedizin_Logo.svg.png" alt="Logo 2" width="150"></td>
  </tr>
</table>

<div style="display: flex; align-items: center;">
  <img src="https://www.beschaeftigte.uni-stuttgart.de/uni-services/oeffentlichkeitsarbeit/corporate-design/cd-dateien/01_Logo/png/unistuttgart_logo_deutsch_cmyk-01.png" alt="Logo 1" width="150" style="margin-right: 10px;">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Bundesanstalt_f%C3%BCr_Arbeitsschutz_und_Arbeitsmedizin_Logo.svg/1024px-Bundesanstalt_f%C3%BCr_Arbeitsschutz_und_Arbeitsmedizin_Logo.svg.png" alt="Logo 2" width="150">
</div>


# RISC - Realistic Imaging for Safety-Critical Cobots

## Overview

The **RISC** project is designed to automate image generation and scene rendering using Blender. The project uses BlenderProc for setting up and rendering 3D scenes, randomizing various scene parameters, and checking for safety constraints. It also saves metadata, such as safety violations and distances, for each generated image. This project is ideal for creating annotated datasets for tasks like computer vision, robotics, or synthetic data generation.

## Key Features

- **Automatic Scene Setup**: Loads and assigns 3D models (e.g., table, workpiece, worker, and panda manipulator) from a `.blend` file.
- **Parameter Randomization**: Randomizes the position, size, and orientation of objects in the scene for variation.
- **Collision and Safety Checking**: Includes logic to check for collisions between specific objects and enforce safety zones.
- **Rendering and Annotation**: Renders images and segmentation maps and logs metadata in CSV format for easy analysis.
- **Documentation Generation**: Uses `pdoc` to generate documentation from inline docstrings.

## Directory Structure

```plaintext
RISC/
│
├── ImageGenerator.py          # Main script for rendering pipeline
├── config.json                # Configuration file with rendering and scene parameters
├── README.md                  # Project documentation
├── UserManual.md              # User Manual for the config file
├── requirements.txt           # requirements specs
│
├── Scenes/
│   ├── textures
│   ├── scene.blend            # Scene with Gripper for Pick and Place Tasks
│   ├── sceneDrilling.blend    # Scene with Drilling Head           
│   └── sceneWelding.blend     # Scene with Welding Head
│
└── venv/                      # Python virtual environment (optional)
```

## Setup

### Prerequisites

- **Python 3.10**: The project uses Python to interact with Blender and render scenes.


### Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/mbsa-tud/RISC
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

4. **Add Scene Folder to Directory**: Paste the `Scene` Folder in your directory.

5. **Configure the Project**: Update `config.json` with your desired rendering parameters, file paths, and randomization ranges. See more in [User Manual.](UserManual.md)

## Usage

Before running the main rendering pipeline, you have to adjust the `config.json`:

### Configuration Parameters
- **SceneParameters**:
    - `SceneSelection`: Name of the Blender (.blend) file to load.
    - `Camera`: Defines camera properties, including distance, resolution, and focal length.
    - `Manipulator`: Contains TCP motion range settings for Panda manipulation.
    - `Human`: Range values for randomizing worker arm positions and location.
- **RenderingParameters**:
    - `NumberImages`: Number of images to render per run.
    - `OutputDir`: Directory to save rendered images and CSV logs.
- **LabelParameters**:
    - `CategoryIDs`: Dictionary mapping object names to category IDs for segmentation.

For more information on how to adjust the `config.json` parameters, please see [User Manual.](UserManual.md)

### Running the Image Generator Pipeline

To run the main script, execute the following statement in your terminal.

```bash
blenderproc run ImageGenerator.py
```

You will see the current progress in your console. Running this script will automatically create a folder `output`, where the generated images and annotations will be saved.

### Visualizing the COCO-Annotations

To visualize the coco-annotations of a certain image, run in your terminal:

```bash
blenderproc vis coco -b output -i <Number of your image> -c coco_annotations.json
```

This will open a new window with the bounding boxes and segmentation masks within the image.

### Documentation Generation

You can generate HTML documentation from docstrings using `pdoc`.
Install by running the following pip command:

```bash
pip install pdoc
```

#### Using pdoc

To generate and view documentation in HTML format, run:

```bash
pdoc ImageGenerator.py -o docs
```

This will save the documentation in the `docs` folder.

If you want to open it directly in your Browser, run:

```bash
pdoc ImageGenerator.py
```

## Code Overview

### Main Modules and Functions

- **`load_config`**: Loads settings from `config.json` to control the pipeline.
- **`load_scene_from_blend`**: Loads objects from a Blender `.blend` file and categorizes them for easy access.
- **`randomize_*` functions**: Randomizes object properties (e.g., position, rotation) to introduce variability across renders.
- **`collision_check_*` functions**: Checks for collisions to prevent overlaps of objects and identifies safety zone violations.
- **`render_scene`**: Renders the scene and saves both images and segmentation maps.
- **`log_to_csv`**: Logs metadata (e.g., violation flags, distances) to a CSV file for each image.

### Main Script: `ImageGenerator.py`

The main script initializes the rendering environment, loads configurations, sets up the scene, performs randomization, checks for safety violations, renders images, and logs metadata. This script iterates through the specified number of images to generate a diverse set of renders.

## Example Workflow

1. **Set up** the `config.json` file with your preferred parameters.
2. **Run** the `ImageGenerator.py` script to generate images in bulk with varied parameters.
3. **View** generated images and analyze metadata in `rendered_data.csv`.
4. **Generate documentation** to understand the codebase, if needed.

## Contributing

If you'd like to contribute, please fork the repository and make changes as you'd like. Pull requests are warmly welcome.

1. Fork this repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.
