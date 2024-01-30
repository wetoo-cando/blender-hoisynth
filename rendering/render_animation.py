import blenderproc as bproc
from blenderproc.python.types.MeshObjectUtility import convert_to_meshes
from blenderproc.python.utility.CollisionUtility import CollisionUtility
import bpy
import os
import coloredlogs, logging
import sys
sys.path.append(os.path.abspath('examples/rendering'))
from config import render_config_test as render_config
render_config.config_instance.setup_blenderproc_configuration()
import numpy as np
import random
import datetime
import mathutils
import transforms3d as t3d
import bmesh
from mathutils import Vector
import argparse

cycles_prefs = bpy.context.preferences.addons['cycles'].preferences
for device_type in ('OPTIX', 'OPENCL'):
    if device_type in cycles_prefs.compute_device_type:
        cycles_prefs.compute_device_type = device_type
        break
for device in cycles_prefs.devices:
    device.use = True

def update_ignore_list_with_indices(indices, current_ignore_list):
    index_to_name = {
        1: 'master_chef_can',
        2: 'cracker_box',
        3: 'sugar_box',
        4: 'tomato_soup_can',
        5: 'mustard_bottle',
        6: 'tuna_fish_can',
        7: 'pudding_box',
        8: 'gelatin_box',
        9: 'potted_meat_can',
        10: 'banana',
        11: 'pitcher_base',
        12: 'bleach_cleanser',
        13: 'bowl',
        14: 'mug',
        15: 'power_drill',
        16: 'wood_block',
        17: 'scissors',
        18: 'large_marker',
        19: 'extra_large_clamp',
        20: 'extra_large_clamp',
        21: 'foam_brick'
    }

    all_mesh_names = list(index_to_name.values())
    mesh_names_to_keep = [index_to_name[idx] for idx in indices if idx in index_to_name]
    meshes_to_ignore = [name for name in all_mesh_names if name not in mesh_names_to_keep]
    updated_ignore_list=current_ignore_list+meshes_to_ignore
    updated_ignore_list = list(set(updated_ignore_list))
    return updated_ignore_list

def is_colliding(new_obj, existing_objs):
    for existing_obj in existing_objs:
        if CollisionUtility.check_bb_intersection(new_obj, existing_obj):
            return True
    return False

def set_pose_for_object(obj_name, obj):
    if obj_name == "box":
        rotation_z = np.random.uniform(0, 2*np.pi)
        obj.set_rotation_euler([0, 0, rotation_z])
    elif obj_name == "realsense_cam":
        direction = mathutils.Vector((0.26369, -0.5599, 0.0125)) - mathutils.Vector(obj.get_location().tolist())
        rot_quat = direction.to_track_quat('Z', 'Y')
        euler_rotation = rot_quat.to_euler()
        obj.set_rotation_euler(list(euler_rotation))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend_dir", type=str, default='/home/blendfiles')
    parser.add_argument("--assets_dir", type=str, default='/home/blender-hoisynth/assets')
    parser.add_argument("--pose_dir", type=str, default='/home/blender-hoisynth/assets/initial_positions')
    parser.add_argument('--output_folder', type=str, default='/home/blender-hoisynth/BlenderProc/output')
    parser.add_argument('--Subject_id', type=str, default='test')
    parser.add_argument('--hand_armature', type=str, default='0_Armature_rotate_coord_right.004')
    return parser.parse_args()

args=parse_args()
assets_folder=args.assets_dir
initial_positions=args.pose_dir
blend_folder=args.blend_dir
for i in range (len(render_config.config_instance.blendfiles)):
    render_config.config_instance.chosen_blendfile= str(i)
    loaded_mesh_objects=[]
    ignore_list=[]
    background_example_objs=[]
    allowed_category_ids=[]
    blend_path=os.path.join(blend_folder,render_config.config_instance.blendfilename)
    blend_file="_".join(blend_path.split('/')[-1].split('.')[0].split('_')[:2])
    ## load objects to be rendered
    with np.load(os.path.join(initial_positions,blend_file+'.npz')) as data:
        allowed_category_ids = data['ycb_ids'].tolist()
    logger = logging.getLogger(__name__)
    # logging.basicConfig(format='%(levelname)s:%(message)s', level=logger.debug)
    coloredlogs.install(level='DEBUG', logger=logger,
                        fmt="%(asctime)s %(filename)s::%(funcName)s: %(levelname)-8s %(message)s")
    ignore_list = update_ignore_list_with_indices(allowed_category_ids, render_config.ignore_obj_by_name)
    loaded_mesh_objects = bproc.loader.load_blend(os.path.join(blend_folder,render_config.config_instance.blendfilename), 
                            obj_types=['empty', 'light', 'armature', 'mesh','camera'], 
                            ignore_obj_by_name = ignore_list,
                            data_blocks="objects")
    logger.warning(f"{len(loaded_mesh_objects)} objects loaded from blendfile: {[loaded_mesh_object.get_name() for loaded_mesh_object in loaded_mesh_objects]}")
    logger.warning(f"... loaded from blendfile: {os.path.join(blend_folder,render_config.config_instance.blendfilename)}")
    for mesh in loaded_mesh_objects:
        print(mesh.get_name())
    # exit()


    # randomly import background objs
    background_folder=os.path.join(assets_folder, 'background_obj')
    background_files = ["bulb.blend", "realsense_cam.blend", "box.blend"]
    ranges = {
        "box": [[[1.58682,3.34652], [-4.3465, 2.3465], [-0.88968, -0.88968]],
                [[-3.3465, 1.58682], [-4.3465, -3.2048], [-0.88968, -0.88968]],
                [[-3.3465, -1.7779], [-3.2048, 2.3465], [-0.88968, -0.88968]]],
        "bulb": [[[-3.5 ,3.5 ], [-4.5 , 2.5],[1.5,1.7]]],
        "realsense_cam": [[[-0.32131 ,0.84869], [-1.6429 , 0.5211], [0.64, 1.24 ]],
                        [[-0.321311 ,0.848689], [-0.0789,0.5211], [0.0375 , 0.64]],
                        [[-0.321311 ,0.848689], [-1.6429, -1.0429], [0.0375 , 0.64]]]
    }
    background_const_objs_path=os.path.join(assets_folder, 'background_example/background.blend')
    background_example_objs = bproc.loader.load_blend(background_const_objs_path,obj_types=['empty', 'light', 'armature', 'mesh','camera'],data_blocks='objects')
    all_loaded_objects=[]
    armature = None

    for new_obj in background_example_objs:
        bpy_obj=bpy.data.objects[new_obj.get_name()]
        # If the object is an armature, set random rotations for its bones
        if bpy_obj.type == "ARMATURE":
            bpy.context.view_layer.objects.active = bpy_obj
            bpy.ops.object.mode_set(mode='POSE')
            
            for bone in bpy_obj.pose.bones:
                random_rotation_y = np.radians(np.random.uniform(-90, 90))  # Convert to radians
                bone.rotation_euler[1] = random_rotation_y  # Y-axis rotation
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.view_layer.objects.active = None
        else:
            all_loaded_objects.append(new_obj)

    selected_files = random.sample(background_files, random.randint(3, len(background_files)))

    for f in selected_files:
        background_objs = bproc.loader.load_blend(os.path.join(background_folder, f))
        obj_name = f.split(".")[0]
        print(background_objs)
        for obj in background_objs:
            num_duplications = random.randint(0,8)
            
            for _ in range(num_duplications):
                duplicated_obj = obj.duplicate()

                collision = True
                attempts = 0
                while collision and attempts < 10: 
                    loc_range = random.choice(ranges[obj_name])
                    loc = [random.uniform(*dim) for dim in loc_range]  
                    rotation_euler = [np.random.uniform(0, 2*np.pi) for _ in range(3)]
                    
                    duplicated_obj.set_location(loc)
                    set_pose_for_object(obj_name, duplicated_obj)

                    if not is_colliding(duplicated_obj, all_loaded_objects):
                        collision = False
                    attempts += 1
                if not collision:
                    all_loaded_objects.append(duplicated_obj)
                else:
                    duplicated_obj.delete()
            obj.delete()
        for obj in all_loaded_objects:
            obj.set_cp("category_id", 0)

    #### load hand bones
    hand_armature_name = args.hand_armature
    hand = bpy.data.objects[hand_armature_name]
    now = datetime.datetime.now()
    time_string = now.strftime('%Y%m%d_%H%M%S')

    # mesh_objects = convert_to_meshes(bpy.data.objects)
    idxs_to_remove = []
    for idx, mesh_object in enumerate(loaded_mesh_objects):
        category_id = None
        # if 'decimated' in mesh_object.get_name():
        #     logger.error(f"How can a decimated obj be in this list? {mesh_object.get_name()}")
        #     continue
        # if 'Desk' in mesh_object.get_name():
        #     mesh_object.set_cp("category_id", 0)
        if 'master_chef' in mesh_object.get_name():
            category_id = 1
            logger.warning(f"Setting category_id to 1 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 1)
        elif 'cracker' in mesh_object.get_name():
            category_id = 2
            logger.warning(f"Setting category_id to 2 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 2)
        elif 'sugar' in mesh_object.get_name():
            category_id = 3
            logger.warning(f"Setting category_id to 3 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 3)
        elif 'tomato_soup' in mesh_object.get_name():
            category_id = 4
            logger.warning(f"Setting category_id to 4 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 4)#
        elif 'mustard' in mesh_object.get_name():
            category_id = 5
            logger.warning(f"Setting category_id to 5 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 5)#
        elif 'tuna' in mesh_object.get_name():
            category_id = 6
            logger.warning(f"Setting category_id to 6 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 6)
        elif 'pudding' in mesh_object.get_name():
            category_id = 7
            logger.warning(f"Setting category_id to 7 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 7)
        elif 'gelatin' in mesh_object.get_name():
            category_id = 8
            logger.warning(f"Setting category_id to 8 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 8)
        elif 'potted_meat' in mesh_object.get_name():
            category_id = 9
            logger.warning(f"Setting category_id to 9 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 9)
        elif 'banana' in mesh_object.get_name():
            category_id = 10
            logger.warning(f"Setting category_id to 10 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 10)
        elif 'pitcher' in mesh_object.get_name():
            category_id = 11
            logger.warning(f"Setting category_id to 11 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 11)#
        elif 'bleach' in mesh_object.get_name():
            category_id = 12
            logger.warning(f"Setting category_id to 12 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 12)#
        elif 'bowl' in mesh_object.get_name():
            category_id = 13
            logger.warning(f"Setting category_id to 13 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 13)
        elif 'mug' in mesh_object.get_name():
            category_id = 14
            logger.warning(f"Setting category_id to 14 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 14)
        elif 'power_drill' in mesh_object.get_name():
            category_id = 15
            logger.warning(f"Setting category_id to 15 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 15)
        elif 'wood' in mesh_object.get_name():
            category_id = 16
            logger.warning(f"Setting category_id to 16 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 16)
        elif 'scissors' in mesh_object.get_name():
            category_id = 17
            logger.warning(f"Setting category_id to 17 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 17)
        elif 'large_marker' in mesh_object.get_name():
            category_id = 18
            logger.warning(f"Setting category_id to 18 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 18)
        elif 'extra_large_clamp' in mesh_object.get_name(): # CAREFUL: this is not the same as 'large_clamp' !!!
            category_id = 20
            logger.warning(f"Setting category_id to 20 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 20)
        elif 'large_clamp' in mesh_object.get_name():
            category_id = 19
            logger.warning(f"Setting category_id to 19 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 19)    
        elif 'foam_brick' in mesh_object.get_name():
            category_id = 21
            logger.warning(f"Setting category_id to 21 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 21)
        elif 'Hand' in mesh_object.get_name():
            category_id = 255
            logger.warning(f"Setting category_id to 255 for {mesh_object.get_name()}")
            mesh_object.set_cp("category_id", 255)    
        else:
            mesh_object.set_cp("category_id", -1)
            category_id = -1
            idxs_to_remove.append(idx)


        if category_id not in allowed_category_ids:
            idxs_to_remove.append(idx)
            continue

        
    logger.error(f"------Removing {len(idxs_to_remove)} non-dex objects from loaded_mesh_objects------")
    for idx_to_remove in idxs_to_remove[::-1]:    
        logger.error(f"Removing {loaded_mesh_objects[idx_to_remove].get_name()}")
    loaded_mesh_objects = [loaded_mesh_objects[i] for i in range(len(loaded_mesh_objects)) if i not in idxs_to_remove]

    loaded_blender_objects = [bpy.data.objects[mesh_obj.get_name()] for mesh_obj in loaded_mesh_objects]
    
    for i_frame_start, frame_start in enumerate(render_config.config_instance.frame_start):    
        num_frames = render_config.config_instance.num_frames[i_frame_start]
        logger.debug(f"[render_recorded_animations.py] frame_start = {frame_start}, num_frames = {num_frames} in steps of {render_config.config_instance.step} ")
        logger.debug(f"[render_recorded_animations.py] rendering frames from {frame_start} to {frame_start+num_frames-1} in steps of {render_config.config_instance.step} ")
        if num_frames is None:
            objs_with_action = [obj for obj in bpy.data.objects if (obj.animation_data is not None
                                                                    and obj.animation_data.action is not None)]
            logger.debug(f"[render_recorded_animations.py] objs_with_action = {objs_with_action}")
            for obj in objs_with_action:
                frames_in_this_obj = int(obj.animation_data.action.frame_range[1])
                logger.debug(f" {num_frames} frames in obj {obj.name}")
                obj_to_export=obj.name
                if frames_in_this_obj > num_frames:
                    num_frames = frames_in_this_obj
                print("look for mesh:")
        for obj in loaded_blender_objects:
            if render_config.config_instance.mesh_export_order[i_frame_start] in obj.name:
                obj_to_export=obj.name
        print("objs_to_export",obj_to_export)
        camera_look_at = convert_to_meshes([bpy.data.objects['lookat_empty']])[0]
        poi = bproc.object.compute_poi([camera_look_at])
            
        if render_config.turn_on_coco_bop_annotations is True:
            bproc.renderer.enable_segmentation_output(map_by=["category_id", "instance", "name"])

        i_cam = 0

        for camera_name in render_config.camera_matrices.keys():
            bpy.context.scene.frame_start = 0
            bpy.context.scene.frame_end = 0
            location = bproc.sampler.part_sphere(poi, 1.0, mode='SURFACE', dist_above_center=0.6, part_sphere_dir_vector=None)
            rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location, inplane_rot=0)
            cam2world_matrix = bproc.math.build_transformation_mat(location, rotation_matrix)

            # Set camera intrinsics
            if 'intrinsic' in render_config.camera_matrices[camera_name].keys():            
                logger.warning(f"Setting camera intrinsics for {i_cam:03d}_{camera_name} from DexYCB cam calibs")
                bproc.camera.set_intrinsics_from_K_matrix(render_config.camera_matrices[camera_name]['intrinsic'], 
                                                        render_config.image_width, render_config.image_height)
            else:
                logger.warning(f"Setting default camera intrinsics for {i_cam:03d}_{camera_name}")
                bproc.camera.set_intrinsics_from_K_matrix(render_config.default_camera_intrinsics, 
                                                            render_config.image_width, render_config.image_height
                                                        )

            # Set camera extrinsics
            if 'extrinsic' in render_config.camera_matrices[camera_name].keys():
                logger.warning(f"Setting camera pose to {i_cam:03d}_{camera_name}")
                bproc.camera.add_camera_pose(render_config.camera_matrices[camera_name]['extrinsic'])
            else:
                logger.warning(f"Setting camera pose to cam2world_matrix")
                bproc.camera.add_camera_pose(cam2world_matrix)

            # output_path = os.path.join(args.output_folder,args.Subject_id,render_config.config_instance.blendfilename.split('.')[0]+time_string)
            output_path = os.path.join(args.output_folder,args.Subject_id,render_config.config_instance.blendfilename.split('.')[0])
            extrinsic_matrix=render_config.camera_matrices[camera_name]['extrinsic']
            intrinsic_matrix=render_config.camera_matrices[camera_name]['intrinsic']
            if num_frames > 72:
                desired_frames = 72
            else:
                desired_frames = num_frames

            step = num_frames / desired_frames
            selected_frames = [round(i * step) + bpy.context.scene.frame_start for i in range(desired_frames)]

            for frame_index,frame_start_ in enumerate(selected_frames):
                frame_end_ = frame_start_ + 1
                logger.debug(f"Rendering frame {frame_start_}")
                bproc.utility.set_keyframe_render_interval(frame_start=frame_start_, frame_end=frame_end_)
                camera_obj = bpy.data.objects["Camera"]

                # Iterate over each frame in the current batch
                for frame in range(frame_start_, frame_end_):
                    
                    bpy.context.scene.frame_set(frame)
                    
                data = bproc.renderer.render(verbose=False)        
                segmaps=np.array(data['category_id_segmaps'])
                

                if render_config.turn_on_coco_bop_annotations is True:
                    bproc.writer.write_bop(os.path.join(args.output_folder,"bop",render_config.config_instance.blendfilename.split('.')[0]+time_string,f'cam{i_cam:03d}_{camera_name}'),
                                        target_objects=loaded_mesh_objects,
                                            depths=data["depth"],
                                            colors=data["colors"],
                                            append_to_existing_output=True,
                                            save_world2cam=True,
                                            m2mm=True,
                                            frames_per_chunk=num_frames)
                    
                    bproc.writer.write_dexycb_data2(os.path.join(output_path, f'{camera_name}'),
                                                frame_index,   
                                                segmaps,
                                                obj_to_export,
                                                extrinsic_matrix,
                                                intrinsic_matrix,
                                                loaded_mesh_objects,
                                                hand,
                                                colors=data["colors"],
                                                depths=data["depth"])                
            i_cam += 1
    saved_cameras = []

    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type != 'CAMERA':
            obj.select_set(True)
            bpy.ops.object.delete()
    bpy.ops.outliner.orphans_purge()
