# Configuration File (`config.json`)

This configuration file controls various settings for the scene, rendering parameters, labeling, and safety constraints.

## Key Descriptions

### Scene Parameters
#### `SceneParameters`

- **`SceneSelection`** (string): Path to the `.blend` file that contains the scene configuration.  
  *Example*: `"Scenes/sceneDrilling.blend"`


- **`Human`**: Configuration for the human model.
  - **`Randomization`** (integer): If set to `1`, the human model is randomized in the scene.
  - **`PositionRange`**: Controls the randomization range of the human’s position.
    - `x`: Array specifying the minimum and maximum x-axis range.  
      *Example*: `[0, 1.5]`  
      _**Note**: This range covers table length._
    - `y`: Array specifying the minimum and maximum y-axis range.  
      *Example*: `[0, -0.35]`  
      _**Note**: Must be bigger than -0.35, otherwise the human collides with the table._
  - **`ArmRangeRight`** (array): Rotation range for the right arm (degrees).  
    *Example*: `[20, -50]`  
    _**Note**: Suggested to leave this range for human-like position._
  - **`ArmRangeLeft`** (array): Rotation range for the left arm (degrees).  
    *Example*: `[-20, 50]`  
    _**Note**: Suggested to leave this range for human-like position._



- **`Manipulator`**: Configuration for the manipulator arm.  
  _**Note**: Below is the maximum range of motion; values should lie within this range._
  - **`Randomization`** (integer): If set to `1`, the manipulator’s position is randomized.
  - **`MotionRange`**: Range of movement allowed for the manipulator’s Tool Center Point (TCP).
    - `x`: Array for the x-axis motion range.  
      *Example*: `[1, 1.8]`  
      _**Note**: Controls forward and backward motion._
    - `y`: Array for the y-axis motion range.  
      *Example*: `[-1, 1]`  
      _**Note**: Controls left and right motion._
    - `z`: Array for the z-axis motion range.  
      *Example*: `[1.65, 2.5]`  
      _**Note**: Controls up and down motion._


- **`Workpiece`**: Configuration for the workpiece object.
  - **`Randomization`** (integer): If `1`, the workpiece will be randomly placed and sized.
  - **`Color`** (array): RGB color values for the workpiece.  
    *Example*: `[0.03, 0.03, 0.03]`  
    _**Note**: RGB values for black are `[0.0, 0.0, 0.0]`, and for white are `[1.0, 1.0, 1.0]`._
  - **`SizeRange`** (object): Range for randomizing workpiece size.
    - `x`: Array for the x-axis size range.  
      *Example*: `[0.5, 1.5]`
    - `y`: Array for the y-axis size range.  
      *Example*: `[0.5, 1.5]`
  - **`PositionRange`** (object): Range for randomizing workpiece position.  
    _**Note**: Below is the maximum area of the table; values should lie within this range._
    - `x`: Array for x-axis position range.  
      *Example*: `[-1, 1.35]`
    - `y`: Array for y-axis position range.  
      *Example*: `[-0.5, 0.8]`


- **`SafetyZone`**: Defines a safety boundary.
  - **`Distance`** (float): Minimum allowable distance in meters for safety between hands and manipulator.  
    *Example*: `0.4`


- **`Camera`**: Configuration for the camera settings.
  - **`FocalLength`** (integer): Focal length of the camera in millimeters.  
    *Example*: `32`
  - **`CameraDistance`** (array): Range for randomizing the camera’s distance from the table center in meters.  
    *Example*: `[3, 7]`
  - **`ImageSize`** (array): Resolution of the output images (width x height in pixels).  
    *Example*: `[720, 720]`

- **`Light`**: Light settings for the scene.
  - **`Type`** (string): Type of light used in the scene.  
    *Example*: `"AREA"`  
    _**Note**: Other types include `"SUN"`, `"POINT"`, and `"SPOT"`._
  - **`Intensity`** (integer): Intensity of the light measured in Watts.  
    *Example*: `1000`

### Rendering Parameters
#### `RenderingParameters`

- **`OutputDir`** (string): Directory to save rendered images and output files.  
  *Example*: `"output"`
- **`NumberImages`** (integer): Number of images to generate in a run.  
  *Example*: `5`


### Labeling Parameters
_**Note**: Should only be changed, when you want to add a new scene; otherwise no need to change anything._

#### `LabelParameters`


- **`CategoryIDs`** (object): Mapping of object names to category IDs for segmentation labeling.
  - `Gripper`, `drillbit`, `weldingbit`, `Panda`: Category `1`.
  - `Armature`, `Gloves`: Category `2`.
  - `Table`: Category `3`.
  - `workpiece`: Category `4`.
  - `SafetyZone`: Category `5`.

