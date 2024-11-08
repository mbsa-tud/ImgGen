import blenderproc as bproc
import bpy
import json
import os
import csv
import numpy as np
from mathutils import Vector
import math


def load_config(config_path):
    """
    Loads the configuration settings from a JSON file.

    Args:
        config_path (str): The file path to the JSON configuration file.

    Returns:
        dict: A dictionary containing the configuration parameters loaded from the JSON file.
    """

    # Open the configuration file and load it as a dictionary
    with open(config_path, 'r') as f:
        config = json.load(f)

    return config


def load_scene_from_blend(file_path, link=False):
    """
    Loads objects from a Blender (.blend) file and categorizes them based on their parent hierarchy.

    Args:
        file_path (str): The file path to the .blend file containing the scene objects.
        link (bool): If True, links the objects; if False, appends them to the current scene.

    Returns:
        dict: A dictionary categorizing loaded objects. Objects are organized into 'Worker' and 'Panda'
              groups based on their parent objects, or stored individually if they have no specific parent.
    """

    # Load objects from the .blend file, either linking or appending based on the `link` parameter
    with bpy.data.libraries.load(file_path, link=link) as (data_from, data_to):
        data_to.objects = data_from.objects  # Load all available objects if no specific filtering is required

    # Dictionary to store categorized objects by their parent groups
    loaded_objects = {"Worker": [], "Panda": []}

    # Iterate through the loaded objects
    for obj in data_to.objects:
        # If not linking, add the object to the current scene collection
        if not link:
            bpy.context.collection.objects.link(obj)

        # Categorize the object based on its parent
        if obj.parent and obj.parent.name == "Worker":
            # Add to 'Worker' group if parent is named "Worker"
            loaded_objects["Worker"].append(obj)
        elif obj.parent and obj.parent.name == "Panda":
            # Add to 'Panda' group if parent is named "Panda"
            loaded_objects["Panda"].append(obj)
        else:
            # For standalone objects without a specific parent, store each individually by its name
            loaded_objects[obj.name] = [obj]

    return loaded_objects


def assign_objects(scene_objects):
    """
    Assigns specific objects from a loaded scene to variables for easier access.

    Args:
        scene_objects (dict): Dictionary containing objects loaded from the scene, organized by name or category.

    Returns:
        tuple: A tuple of assigned objects in the following order:
               (table, workpiece, worker, panda, tcp, environment, gripper)
    """

    # Retrieve and assign the 'Table' object
    table = scene_objects["Table"][0]

    # Retrieve and subdivide the 'workpiece' object for finer geometry manipulation
    workpiece = subdivide_object(scene_objects["workpiece"][0])

    # Retrieve the list of 'Worker' objects
    worker = scene_objects["Worker"]

    # Retrieve the list of 'Panda' objects
    panda = scene_objects["Panda"]

    # Retrieve the 'TCP' (Tool Center Point) object
    tcp = scene_objects["TCP"][0]

    # Retrieve the 'Environment' object
    environment = scene_objects["Environment"][0]

    # Retrieve the 'Gripper' object
    gripper = scene_objects["Gripper"][0]

    return table, workpiece, worker, panda, tcp, environment, gripper


def randomize_camera_and_light(table, config):
    """
    Sets up and randomizes the position of the camera and light in the scene based on configuration parameters.

    Args:
        table: The table object, used as a reference point for positioning the camera.
        config (dict): Configuration dictionary containing parameters for camera distance, resolution,
                       focal length, and light properties.
    """

    # Get camera distance range from config and calculate the table's center position in the scene
    camera_distance = config["SceneParameters"]["Camera"]["CameraDistance"]
    table_center = (table.location.x, table.location.y, table.dimensions[2])

    # Camera position randomization within specified distance and orientation limits
    camera_location = bproc.sampler.shell(
        center=table_center,
        radius_min=camera_distance[0],
        radius_max=camera_distance[1],
        elevation_min=10, elevation_max=40,
        azimuth_min=-180, azimuth_max=180,
        uniform_volume=True
    )
    # Calculate rotation matrix to make the camera face the table center
    camera_rotation_matrix = bproc.camera.rotation_from_forward_vec(table_center - camera_location)

    # Generate transformation matrix to position and orient the camera in the scene
    cam2world_matrix = bproc.math.build_transformation_mat(camera_location, camera_rotation_matrix)
    bproc.camera.add_camera_pose(cam2world_matrix)

    # Set camera resolution based on config
    image_size = config["SceneParameters"]["Camera"]["ImageSize"]
    bproc.camera.set_resolution(image_size[0], image_size[1])

    # Adjust focal length if a camera object exists
    camera = bpy.data.objects.get("Camera")
    if camera and camera.type == 'CAMERA':
        camera.data.lens = config["SceneParameters"]["Camera"]["FocalLength"]
    else:
        print("Camera object not found or not set to type CAMERA.")

    # Light setup: configure intensity, type, and position
    light = bproc.types.Light()
    light.set_energy(config["SceneParameters"]["Light"]["Intensity"])
    light.set_type(config["SceneParameters"]["Light"]["Type"])
    # Offset light from camera location for better scene lighting
    light.set_location(camera_location + np.array([1, -1, 2]))


def randomize_position(obj, range_x, range_y, range_z=None):
    """
    Randomizes the location of an object within specified x, y, and optional z ranges.

    Args:
        obj: The Blender object whose position will be randomized.
        range_x (tuple): The range (min, max) for the x-axis.
        range_y (tuple): The range (min, max) for the y-axis.
        range_z (tuple, optional): The range (min, max) for the z-axis. If None, z-axis position is not modified.
    """
    # Set the x-axis position randomly within the specified range
    obj.location.x = np.random.uniform(*range_x)

    # Set the y-axis position randomly within the specified range
    obj.location.y = np.random.uniform(*range_y)

    # Set the z-axis position randomly if a range is provided
    if range_z:
        obj.location.z = np.random.uniform(*range_z)


def randomize_panda(tcp, config):
    """
    Randomizes the position of the Tool Center Point (TCP) of the Panda manipulator
    based on the configuration's motion range.

    Args:
        tcp: The TCP object whose position will be randomized.
        config (dict): Configuration dictionary containing motion range for the TCP.

    Returns:
        tcp: The modified TCP object with its position randomized.
    """

    # Extract the motion range for the TCP from the configuration
    tcp_cfg = config["SceneParameters"]["Manipulator"]["MotionRange"]

    # Randomize the TCP's position within the specified x, y, and z ranges
    randomize_position(tcp, tcp_cfg["x"], tcp_cfg["y"], tcp_cfg["z"])


def randomize_workpiece(workpiece, config):
    """
    Randomizes the size, rotation, and position of the workpiece based on configuration parameters.

    Args:
        workpiece: The workpiece object to be randomized.
        config (dict): Configuration dictionary containing ranges for workpiece size, rotation, and position.

    Returns:
        workpiece: The modified workpiece object with randomized size, rotation, and position.
    """

    # Extract workpiece configuration details from the config dictionary
    workpiece_cfg = config["SceneParameters"]["Workpiece"]

    # Randomize the scale of the workpiece within specified x and y size ranges; z-axis is set to 1 for consistency
    workpiece.scale = (
        np.random.uniform(*workpiece_cfg["SizeRange"]["x"]),
        np.random.uniform(*workpiece_cfg["SizeRange"]["y"]),
        1
    )

    # Set a random rotation for the workpiece on the z-axis, between 0 and 360 degrees
    workpiece.rotation_euler.z = math.radians(np.random.uniform(0, 360))

    # Randomize the workpiece's position within specified x and y ranges, using helper function `randomize_position`
    randomize_position(workpiece, workpiece_cfg["PositionRange"]["x"], workpiece_cfg["PositionRange"]["y"])

    return workpiece


def set_bone_rotation(bone, x, y, z):
    """
    Sets the rotation for a given bone in radians, based on provided rotation angles in degrees.

    Args:
        bone: The bone object whose rotation will be set.
        x (float): Rotation angle around the X-axis in degrees.
        y (float): Rotation angle around the Y-axis in degrees.
        z (float): Rotation angle around the Z-axis in degrees.
    """
    # Set the rotation mode to 'XYZ' to apply rotation in x, y, z order
    bone.rotation_mode = 'XYZ'

    # Apply the specified rotations by converting degrees to radians
    bone.rotation_euler = (math.radians(x), math.radians(y), math.radians(z))


def randomize_worker(worker, config):
    """
    Randomizes the arm positions and location of the worker model based on configuration parameters.

    Args:
        worker: The armature object representing the worker character to be randomized.
        config (dict): Configuration dictionary containing ranges for arm rotations and worker position.

    Returns:
        worker: The modified worker object with randomized arm positions and location.
    """

    # Extract arm configuration details from the configuration dictionary
    arm_cfg = config["SceneParameters"]["Human"]
    armature_obj = worker

    # Set the worker armature object to the active object and switch to 'POSE' mode
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')

    # Dictionary to hold references to the relevant bones for arm and hand movements
    bones = {
        'right_arm': armature_obj.pose.bones.get('mixamorig:RightArm'),
        'right_forearm': armature_obj.pose.bones.get('mixamorig:RightForeArm'),
        'right_hand': armature_obj.pose.bones.get('mixamorig:RightHand'),
        'left_arm': armature_obj.pose.bones.get('mixamorig:LeftArm'),
        'left_forearm': armature_obj.pose.bones.get('mixamorig:LeftForeArm'),
        'left_hand': armature_obj.pose.bones.get('mixamorig:LeftHand')
    }

    # Randomize the rotation of the right arm within specified range from config
    right_rotation = np.random.uniform(*arm_cfg["ArmRangeRight"])
    set_bone_rotation(bones['right_arm'], 70, 11, right_rotation)  # Set right arm rotation
    set_bone_rotation(bones['right_forearm'], 0, 19, -36)  # Set right forearm rotation
    set_bone_rotation(bones['right_hand'], 6, -67, 0)  # Set right hand rotation

    # Randomize the rotation of the left arm within specified range from config
    left_rotation = np.random.uniform(*arm_cfg["ArmRangeLeft"])
    set_bone_rotation(bones['left_arm'], 70, -11, left_rotation)  # Set left arm rotation
    set_bone_rotation(bones['left_forearm'], 0, -19, 36)  # Set left forearm rotation
    set_bone_rotation(bones['left_hand'], 6, 67, 0)  # Set left hand rotation

    # Switch back to 'OBJECT' mode after setting bone rotations
    bpy.ops.object.mode_set(mode='OBJECT')

    # Randomize the overall position of the worker within specified x and y position ranges
    randomize_position(worker, arm_cfg["PositionRange"]["x"], arm_cfg["PositionRange"]["y"])


def subdivide_object(obj, cuts=10):
    """
    Subdivides the faces of an object to increase its vertex count, which can improve precision
    for collision detection.

    Args:
        obj: The Blender object to be subdivided.
        cuts (int): Number of cuts to make in the subdivision, which controls the density of vertices.

    Returns:
        obj: The modified object with additional vertices created by subdivision.
    """
    # Set the object as active in the scene to apply operations on it
    bpy.context.view_layer.objects.active = obj

    # Ensure the object is in 'OBJECT' mode before switching to 'EDIT' mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Switch to 'EDIT' mode to perform the subdivision operation
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')

    # Select all faces of the object and subdivide them to increase vertex count
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=cuts)

    # Switch back to 'OBJECT' mode after subdivision
    bpy.ops.object.mode_set(mode='OBJECT')

    return obj


def get_world_bounding_box_xy(obj):
    """
    Calculates the minimum and maximum x and y coordinates of an object's bounding box in world space.

    Args:
        obj: The Blender object whose bounding box is to be calculated.

    Returns:
        tuple: A tuple containing the minimum x, maximum x, minimum y, and maximum y coordinates of the bounding box.
    """
    # Update the scene to ensure transformations are applied before bounding box calculation
    bpy.context.view_layer.update()

    # Get the world-space coordinates of the bounding box corners
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    # Calculate the minimum and maximum x and y coordinates of the bounding box in the XY plane
    min_x = min(corner.x for corner in bbox_corners)
    max_x = max(corner.x for corner in bbox_corners)
    min_y = min(corner.y for corner in bbox_corners)
    max_y = max(corner.y for corner in bbox_corners)

    return min_x, max_x, min_y, max_y


# Function to check if a point is within the 2D area on the XY plane
def is_point_within_xy_area(point, min_x, max_x, min_y, max_y):
    """
    Checks if a point lies within a specified rectangular area on the XY plane.

    Args:
        point: The point to check, represented as a Vector.
        min_x (float): Minimum x-coordinate of the area.
        max_x (float): Maximum x-coordinate of the area.
        min_y (float): Minimum y-coordinate of the area.
        max_y (float): Maximum y-coordinate of the area.

    Returns:
        bool: True if the point lies within the specified area, False otherwise.
    """
    return min_x <= point.x <= max_x and min_y <= point.y <= max_y


def collision_check_objects(obj1, obj2):
    """
    Checks for a collision between two objects by verifying if any vertices of obj1 lie within
    the bounding box of obj2 on the XY plane.

    Args:
        obj1: The first object (typically a mesh) whose vertices are checked for collision.
        obj2: The second object whose bounding box defines the collision area.

    Returns:
        bool: True if a collision is detected, otherwise False.
    """
    # Ensure obj1 exists and is a mesh before checking
    if obj1 and obj1.type == 'MESH':
        # Update object from edit mode to apply transformations to vertices
        obj1.update_from_editmode()

        # Get the bounding box coordinates of obj2 in the XY plane
        area_min_x, area_max_x, area_min_y, area_max_y = get_world_bounding_box_xy(obj2)

        # Iterate over each vertex in obj1's mesh data
        for vertex in obj1.data.vertices:
            # Calculate the vertex's location in world space
            world_vertex = obj1.matrix_world @ vertex.co

            # Check if the vertex lies within the bounding box area in the XY plane
            if is_point_within_xy_area(world_vertex, area_min_x, area_max_x, area_min_y, area_max_y):
                return True  # Collision detected

        return False  # No collision detected
    else:
        # Print an error message if obj1 is not found or is not a mesh
        print("Object not found or is not a mesh.")
        return False


def collision_check_scene(workpiece, config):
    """
    Continuously checks for collisions between the workpiece and specific objects in the scene,
    randomizing the workpiece's position if a collision is detected.

    Args:
        workpiece: The workpiece object to check for collisions.
        config (dict): Configuration dictionary containing randomization parameters for the workpiece.
    """
    # Retrieve reference objects from the scene for collision checking
    vest = bpy.data.objects.get('Ch17_Vest')
    panda_leg = bpy.data.objects.get('Link-0')

    # Initial collision checks for the workpiece against the vest and panda_leg
    check1 = collision_check_objects(workpiece, vest)
    check2 = collision_check_objects(workpiece, panda_leg)

    # If a collision is detected, randomize workpiece position and re-check until no collision
    while check1 or check2:
        # Randomize workpiece's position based on config
        workpiece = randomize_workpiece(workpiece, config)

        # Re-check collisions after repositioning
        check1 = collision_check_objects(workpiece, vest)
        check2 = collision_check_objects(workpiece, panda_leg)


def get_evaluated_vertices_in_world_space(obj):
    """
    Returns a list of the object's vertices in world coordinates, including all modifiers
    and poses applied, by accessing the evaluated dependency graph version of the object.

    Args:
        obj: The Blender object for which to retrieve evaluated vertices.

    Returns:
        list: A list of vertices in world coordinates with all transformations applied,
              or None if the object is not a mesh.
    """
    # Check if the object is of type 'MESH', return None if it's not
    if obj.type != 'MESH':
        print("Object is not a mesh.")
        return None

    # Update the scene dependency graph to ensure all transformations are applied
    bpy.context.view_layer.update()

    # Access the evaluated version of the object, which includes all applied modifiers
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()

    # Convert each vertex to world coordinates and store in a list
    vertices_world_space = [eval_obj.matrix_world @ v.co for v in mesh.vertices]

    # Clear the evaluated mesh to free memory and avoid leaks
    eval_obj.to_mesh_clear()

    return vertices_world_space


def find_closest_distance_between_objects(obj1, obj2):
    """
    Finds and returns the shortest distance between vertices of two objects, with all
    transformations, modifiers, and poses applied.

    Args:
        obj1: The first Blender object to compare.
        obj2: The second Blender object to compare.

    Returns:
        float: The minimum distance between the two objects' vertices.
               If either object is not a mesh, returns None.
    """
    # Check if both objects exist and are of type 'MESH', otherwise return None
    if not obj1 or not obj2 or obj1.type != 'MESH' or obj2.type != 'MESH':
        print("Both objects must be mesh types.")
        return None

    # Get the evaluated world-space vertices for both objects
    obj1_vertices = get_evaluated_vertices_in_world_space(obj1)
    obj2_vertices = get_evaluated_vertices_in_world_space(obj2)

    # Initialize minimum distance with a very large value and placeholders for closest points
    min_distance = float('inf')

    # Calculate the minimum distance between any vertex in obj1 and any vertex in obj2
    for v1 in obj1_vertices:
        for v2 in obj2_vertices:
            # Calculate the Euclidean distance between two vertices
            distance = (v1 - v2).length
            # Update minimum distance if the calculated distance is smaller
            if distance < min_distance:
                min_distance = distance

    return min_distance


def safety_check(config):
    """
    Checks if the distance between the 'Hand' and 'Gloves' objects in the scene is within
    a defined safety threshold.

    Args:
        config (dict): Configuration dictionary containing the safety zone distance parameter.

    Returns:
        tuple: A tuple containing:
            - violation (int): 1 if the minimum distance is less than the safety threshold, 0 otherwise.
            - min_distance (float): The minimum measured distance between the 'Hand' and 'Gloves' objects.
    """
    # Retrieve the 'Hand' and 'Gloves' objects from the scene
    hand = bpy.data.objects.get("Hand")
    gloves = bpy.data.objects.get("Gloves")

    # Calculate the minimum distance between 'Hand' and 'Gloves'
    min_distance = find_closest_distance_between_objects(hand, gloves)

    # Check if the distance violates the safety threshold specified in the config
    if min_distance < config["SceneParameters"]["SafetyZone"]["Distance"]:
        violation = 1  # Violation detected
    else:
        violation = 0  # No violation

    return violation, min_distance


def assign_category_ids(category_dict):
    """
    Assigns category IDs to objects in the Blender scene based on a provided dictionary,
    which maps object names to category IDs.

    Args:
        category_dict (dict): A dictionary mapping object names (keys) to category IDs (values).
    """
    # Loop through all objects in the Blender scene
    for obj in bpy.data.objects:
        # Check if the object's name is in the category dictionary
        if obj.name in category_dict:
            # Assign the corresponding category ID to the object
            obj['category_id'] = category_dict[obj.name]


def render_scene(config):
    """
    Renders the scene and saves both the rendered images and segmentation maps in the specified output directory.
    Assigns category IDs to objects in the scene for segmentation before rendering.

    Args:
        config (dict): Configuration dictionary containing label parameters, rendering settings,
                       and the output directory path.
    """
    # Extract category IDs from config and assign to scene objects
    categories = config["LabelParameters"]["CategoryIDs"]
    assign_category_ids(categories)

    # Set the output directory for saving render results
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, config["RenderingParameters"]["OutputDir"])

    # Set the maximum amount of samples for rendering quality; default is 1024, here set to 128 for faster rendering
    bproc.renderer.set_max_amount_of_samples(128)

    # Render the scene and generate segmentation maps
    data = bproc.renderer.render()
    seg_data = bproc.renderer.render_segmap(
        map_by=["instance", "class", "name"],
        default_values={"category_id": 0, "class_label": 'background'}
    )

    # Save rendered images and segmentation maps as COCO annotations
    bproc.writer.write_coco_annotations(
        output_dir=output_dir,
        instance_segmaps=seg_data["instance_segmaps"],
        instance_attribute_maps=seg_data["instance_attribute_maps"],
        colors=data["colors"],
        color_file_format="JPEG",
        jpg_quality=100,
        append_to_existing_output=True,
        file_prefix="image_",
        indent=2
    )


def log_to_csv(violation, distance, i, config):
    """
    Logs rendering information to a CSV file, including image name, safety violation status, and distance.
    If the CSV file already exists, continues numbering images based on the last entry.

    Args:
        violation (int): Safety violation flag (1 if violation detected, 0 otherwise).
        distance (float): Minimum distance between 'Hand' and 'Gloves' objects.
        i (int): Index for the image, used in the image file name if starting fresh.
        config (dict): Configuration dictionary containing the output directory path.
    """
    # Set the output directory for the CSV file based on config
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, config["RenderingParameters"]["OutputDir"])

    csv_file = os.path.join(output_dir, "rendered_data.csv")

    # Initialize the starting image index
    if os.path.exists(csv_file):
        # Open the file in read mode to get the last entry
        with open(csv_file, mode="r") as file:
            reader = csv.reader(file)
            rows = list(reader)
            # Check if there are rows beyond the header and get the last row's index
            if len(rows) > 1:
                last_row = rows[-1]
                # Extract the last image number and increment it
                last_image_num = int(last_row[0].split('_')[1].split('.')[0])
                i = last_image_num + 1
    else:
        # If the file doesn't exist, start numbering from the provided index `i`
        i = i

    # Format the image name with leading zeros
    image_name = f"image_{i:06d}.jpg"  # This will format the index `i` to six digits with leading zeros

    # Write rendering data to CSV, including headers if file is newly created
    with open(csv_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            # Write CSV header if file is empty
            writer.writerow(["ImageName", "Violation", "Distance"])
        # Write image information (name, violation, and distance) to the CSV
        writer.writerow([image_name, violation, distance])

    print(f"Rendered and saved image data for {image_name} to CSV")


def cleanup_scene():
    """
    Deletes all objects in the Blender scene except for cameras and lights,
    ensuring a clean scene for subsequent operations.
    """
    # Deselect all objects in the scene
    bpy.ops.object.select_all(action='DESELECT')

    # Select only objects that are not cameras or lights
    for obj in bpy.context.scene.objects:
        if obj.type not in {'CAMERA', 'LIGHT'}:
            obj.select_set(True)

    # Delete selected objects to clear the scene
    bpy.ops.object.delete()


def main():
    """
    Main function to initialize the rendering pipeline, load the configuration, set up the scene,
    randomize parameters, check for collisions and safety, render the scene, log data, and finally clean up.
    """
    # Initialize the BlenderProc environment
    bproc.init()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Load configuration settings from the specified path
    config_path = "config.json"
    config_path = os.path.join(base_dir, config_path)
    config = load_config(config_path)

    # Loop through the specified number of images to render
    num_images = config["RenderingParameters"]["NumberImages"]
    for i in range(num_images):
        # Reset keyframes for each render to ensure there are no leftover animations
        bproc.utility.reset_keyframes()

        # Load the scene objects from a .blend file based on the configuration
        scene_file_path = os.path.join(base_dir, config["SceneParameters"]["SceneSelection"])
        scene_objects = load_scene_from_blend(file_path=scene_file_path)

        # Assign specific objects from the loaded scene for easy reference
        table, workpiece, worker, panda, tcp, environment, gripper = assign_objects(scene_objects)

        # Randomize the camera position and lighting based on the table's location
        randomize_camera_and_light(table, config)

        # Randomize the positions and rotations of the main objects in the scene
        randomize_panda(tcp, config)  # Randomize the Panda's Tool Center Point (TCP)
        workpiece = randomize_workpiece(workpiece, config)  # Randomize workpiece size, rotation, and position
        randomize_worker(worker[0], config)  # Randomize the worker's arm positions and location

        # Update the scene to apply transformations before collision checks
        bpy.context.view_layer.update()

        # Check for collisions in the scene and reposition the workpiece if necessary
        collision_check_scene(workpiece, config)

        # Perform a safety check by measuring the distance between key objects (Hand and Gloves)
        violation, distance = safety_check(config)

        # Render the scene and generate annotations for segmentation
        render_scene(config)

        # Log information about the render to a CSV file
        log_to_csv(violation, distance, i, config)

        # Clean up the scene by removing all objects except cameras and lights
        cleanup_scene()


if __name__ == "__main__":
    main()
