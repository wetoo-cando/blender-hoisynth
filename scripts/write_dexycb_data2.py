
import png
import os
import shutil
from typing import Optional, Dict, Union, Tuple, List
import numpy as np
import cv2
import bpy
import math
from scipy.spatial.transform import Rotation   
import transforms3d
from blenderproc.python.types.MeshObjectUtility import MeshObject, get_all_mesh_objects
from blenderproc.python.utility.Utility import Utility, resolve_path
from mathutils import Euler

def write_dexycb_data2(output_dir: str,frame_index,segmaps,obj_to_export,extrinsic,intrinsic,loaded_mesh_objects,hand: Optional[List[np.ndarray]] = None,
                           colors: Optional[List[np.ndarray]] = None, color_file_format: str = "JPEG",rgb_output_key: str = "colors",depths: Optional[List[np.ndarray]] = None,jpg_quality: int = 95,file_prefix: str = ""):
    colors = [] if colors is None else list(colors)
    depths =[] if depths is None else list(depths)
    intrinsic=np.array(intrinsic)
    if len(colors[0].shape) == 4:
        raise ValueError(f"BlenderProc currently does not support writing coco annotations for stereo images. "
                         f"However, you can enter left and right images / segmaps separately.")

    # Create output directory
    os.makedirs(os.path.join(output_dir), exist_ok=True)

    if not colors:
        # Find path pattern of rgb images
        rgb_output = Utility.find_registered_output_by_key(rgb_output_key)
        if rgb_output is None:
            raise RuntimeError(f"There is no output registered with key {rgb_output_key}. Are you sure you "
                               f"ran the RgbRenderer module before?")
        
    loaded_blender_objects = [bpy.data.objects[mesh_obj.get_name()] for mesh_obj in loaded_mesh_objects]

    ## turn to camera coordinate first
    camera_pose_world_for_obj_mesh=np.zeros([4,4])
    camera_pose_world_for_obj_mesh[0,:]=extrinsic[1,:]
    camera_pose_world_for_obj_mesh[1,:]=extrinsic[0,:]
    camera_pose_world_for_obj_mesh[2,:]=extrinsic[2,:]
    camera_pose_world_for_obj_mesh[0,0]=-1*camera_pose_world_for_obj_mesh[0,0]
    camera_pose_world_for_obj_mesh[1,1]=-1*camera_pose_world_for_obj_mesh[1,1]
    camera_pose_world_for_obj_mesh[1,2]=-1*camera_pose_world_for_obj_mesh[1,2]
    camera_pose_world_for_obj_mesh[0,3]=-1*camera_pose_world_for_obj_mesh[0,3]
    camera_pose_world_for_obj_mesh[2,1]=-1*camera_pose_world_for_obj_mesh[2,1]
    camera_pose_world_for_obj_mesh[2,2]=-1*camera_pose_world_for_obj_mesh[2,2]
    camera_pose_world_for_obj_mesh[3,:]=[0,0,0,1]
    
    
    segmaps[segmaps==-1]=0
    segmaps=segmaps.astype(np.uint8)

    # collect all RGB paths
    new_image_paths = []
    frame_poses=[]
    # for each rendered frame
    total_frames=bpy.context.scene.frame_end-bpy.context.scene.frame_start
    if total_frames>72:
        desired_frames=72
    else:
        desired_frames=total_frames
    step=total_frames/desired_frames
    selected_frames=[]
    for i in range(desired_frames):
        selected_frames.append(round(i*step)+bpy.context.scene.frame_start)
    print(selected_frames)

    for frame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end):
        
        if frame in selected_frames:
            frame_num=selected_frames.index(frame)+frame_index
            if colors:
                color_rgb = colors[frame - bpy.context.scene.frame_start]

                # Reverse channel order for opencv
                color_bgr = color_rgb.copy()
                color_bgr[..., :3] = color_bgr[..., :3][..., ::-1]

                if color_file_format == 'PNG':
                    target_base_path = f'color_{file_prefix}{frame_num:06}.png'
                    target_path = os.path.join(output_dir, target_base_path)
                    cv2.imwrite(target_path, color_bgr)
                elif color_file_format == 'JPEG':
                    target_base_path = f'color_{file_prefix}{frame_num:06}.jpg'
                    target_path = os.path.join(output_dir, target_base_path)
                    cv2.imwrite(target_path, color_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), jpg_quality])
                else:
                    raise RuntimeError(f'Unknown color_file_format={color_file_format}. Try "PNG" or "JPEG"')
            else:
                source_path = rgb_output["path"] % frame
                target_base_path = file_prefix + os.path.basename(rgb_output["path"] % (frame))
                target_path = os.path.join(output_dir, target_base_path)
                shutil.copyfile(source_path, target_path)


            if depths:
                depth = depths[frame - bpy.context.scene.frame_start]
                target_base_path = f'aligned_depth_to_color_{file_prefix}{frame_num:06}.png'
                target_path = os.path.join(output_dir, target_base_path)
                depth_mm = 1000.0 * depth  # [m] -> [mm]
                depth_mm[depth_mm > 65535] = 65535
                depth_mm_uint16 = np.round(depth_mm).astype(np.uint16)

                w_depth = png.Writer(depth_mm.shape[1], depth_mm.shape[0], greyscale=True, bitdepth=16)
                with open(target_path, 'wb') as f:
                    w_depth.write(f, np.reshape(depth_mm_uint16, (-1, depth_mm.shape[1])))   


            obj_poses_list = []
            bpy.context.scene.frame_set(frame)  # Set the current frame to compute poses
            #obj_poses = np.float32([compute_6d_pose_in_camera_coords(extrinsic, obj) for obj in loaded_blender_objects])
            for idx,obj in enumerate(loaded_blender_objects):
                obj_pose = compute_6d_pose_in_camera_coords(extrinsic, obj)
                obj_poses_list.append(obj_pose)
                obj_poses=np.array(obj_poses_list, dtype=np.float32)
            obj_poses=obj_poses[::-1, :, :]
            # hands
            
            # 3d pose
            hand_pose_3d=np.float32(get_3d_hand_pose(extrinsic, hand))
            # 2d pose
            hand_pose_2d=np.float32(get_2d_hand_pose(intrinsic,hand_pose_3d))
            
            target_base_path=f'labels_{file_prefix}{frame_num:06}'
            target_path = os.path.join(output_dir, target_base_path)

            # save
            np.savez_compressed(target_path,seg=segmaps[selected_frames.index(frame),:,:],pose_y=obj_poses,joint_3d=hand_pose_3d,joint_2d=hand_pose_2d)


            #if not os.path.exists(obj_save_path):
            #    os.makedirs(obj_save_path)
            #if not os.path.exists(hand_save_path):
            #    os.makedirs(hand_save_path)
            # obj mesh

            for obj in loaded_blender_objects:
                if obj.name==obj_to_export:

                    ## skip this for now
                    continue

                    # begin of the block 
                    # Apply the inverse of the camera's world matrix to the object
                    obj.select_set(True)
                    print(obj.name)
                    duplicate_obj = obj.copy()
                    duplicate_obj.data = obj.data.copy()  

                    bpy.context.collection.objects.link(duplicate_obj)  
                    obj.select_set(False)
                    obj_animation=duplicate_obj.animation_data
                    duplicate_obj.animation_data_clear()
                    duplicate_obj.select_set(True)
                    print(f"Processing object: {obj.name}")
                    obj_matrix_rotation=duplicate_obj.matrix_world
                    obj_euler_rotation = obj_matrix_rotation.to_euler()
                    # to camera coordinate system
                    wRobj=transforms3d.euler.euler2mat(obj_euler_rotation[0],obj_euler_rotation[1],obj_euler_rotation[2]+ math.radians(90))
                    objlocation=duplicate_obj.location
                    wtobj=np.array([-1*objlocation.y,objlocation.x , objlocation.z])
                    wTobj=np.vstack((np.column_stack((wRobj,wtobj)),[0, 0, 0, 1]))
                    print("original rot, loc:",obj_euler_rotation,objlocation)

                    # the transform
                    cTobj=np.dot(np.linalg.inv(camera_pose_world_for_obj_mesh),wTobj)
                    # print("T in camera viwe:",cTobj)

                    cRobj=cTobj[:3,:3]
                    obj_euler=Euler(transforms3d.euler.mat2euler(cRobj),'XYZ')
                    # print("new euler",obj_euler[0])

                    duplicate_obj.location.x=cTobj[0,3]
                    duplicate_obj.location.y=cTobj[1,3]
                    duplicate_obj.location.z=cTobj[2,3]
                    duplicate_obj.rotation_euler.x=obj_euler[0]
                    duplicate_obj.rotation_euler.y=obj_euler[1]
                    duplicate_obj.rotation_euler.z=obj_euler[2]

                    print("transformed rot, loc:",duplicate_obj.rotation_euler,duplicate_obj.location)
                    ## for mesh exporting
                    bpy.context.view_layer.objects.active = duplicate_obj
                    bpy.ops.object.transform_apply(location=True, rotation=True)
                    duplicate_obj.rotation_euler.x+=math.radians(90)

                    # keep the name, just in case more than one obj is left
                    prefix_for_obj = output_dir.split("/output/")[-1].replace("/", "_")
                    #print("active mesh is:",bpy.context.active_object.name)
                    print("selected mesh is:",[obj.name for obj in bpy.context.selected_objects])
                    print("and the rot,loc is:", [obj.rotation_euler for obj in bpy.context.selected_objects],[obj.location for obj in bpy.context.selected_objects])
                    path_to_save = os.path.join(obj_save_path,f"{prefix_for_obj}_{obj.name}_{frame}.obj")
                    # try to apply the matrix directly
                    print("cTobj",cTobj) 

                    # Export the object as .obj
                    bpy.ops.export_scene.obj(filepath=path_to_save, use_selection=True,use_materials=False)
                    bpy.ops.object.delete()


            # hand mesh
            if hand:
                # dont export for now
                continue
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = hand
                hand.select_set(True)
                for child in hand.children:
                    if child.type == 'MESH':
                        if child.name!="Asian_Male_20's_Hand_Neutral_SubD_L1.010":
                            print("there was a mesh",child.name)
                            hand_mesh = child
                            hand_mesh.select_set(True)
                            break
                bpy.ops.object.duplicate()
                # Identify the duplicates from the selected objects
                duplicate_hand = None
                duplicate_mesh = None
                for obj in bpy.context.selected_objects:
                    if obj.type == 'ARMATURE' and obj != hand:
                        duplicate_hand = obj
                    elif obj.type == 'MESH' and obj != hand_mesh:
                        duplicate_mesh = obj

                # Update the Armature Modifier on the duplicated mesh to point to the duplicated armature
                for mod in duplicate_mesh.modifiers:
                    if mod.type == 'ARMATURE' and mod.object == hand:
                        mod.object = duplicate_hand
                # bpy.context.collection.objects.link(duplicate_hand)
                hand_matrix_rotation=duplicate_hand.matrix_world
                hand_euler_rotation = hand_matrix_rotation.to_euler()
                
                hand.select_set(False)
                duplicate_hand.select_set(True)
                # to camera coordinate system
                wRhand=transforms3d.euler.euler2mat(hand_euler_rotation[0],hand_euler_rotation[1],hand_euler_rotation[2]+ math.radians(90))
                handlocation=hand.location
                wthand=np.array([-1*handlocation.y,handlocation.x , handlocation.z])
                wThand=np.vstack((np.column_stack((wRhand,wthand)),[0, 0, 0, 1]))
                # the transform
                cThand=np.dot(np.linalg.inv(camera_pose_world_for_obj_mesh),wThand)
                cRhand=cThand[:3,:3]
                hand_euler=Euler(transforms3d.euler.mat2euler(cRhand),'XYZ')

                duplicate_hand.location.x=cThand[0,3]
                duplicate_hand.location.y=cThand[1,3]
                duplicate_hand.location.z=cThand[2,3]
                duplicate_hand.rotation_euler.x=hand_euler[0]
                duplicate_hand.rotation_euler.y=hand_euler[1]
                duplicate_hand.rotation_euler.z=hand_euler[2]
                bpy.context.view_layer.objects.active = duplicate_hand
                bpy.ops.object.transform_apply(location=True, rotation=True)
                duplicate_hand.rotation_euler.x+=math.radians(90)
                for child in duplicate_hand.children:
                    if child.type == 'MESH':
                        if child.name!="Asian_Male_20's_Hand_Neutral_SubD_L1.010":
                            print("there was a mesh",child.name)
                            hand_mesh = child
                            break

                if hand_mesh:
                    hand_mesh.select_set(True)
                    print("start noticing")
                    hand_animation=hand.animation_data
                    print(hand_animation)
                    duplicate_hand.animation_data_clear()

                    prefix_for_hand = output_dir.split("/output/")[-1].replace("/", "_")

                    path_to_save = os.path.join(hand_save_path,f"{prefix_for_hand}_{hand.name}_{frame}.obj")
                    # export
                    bpy.ops.export_scene.obj(filepath=path_to_save, use_selection=True,use_materials=False)
                    print(f"Name: {hand.name}, Type: {hand.type}")
                    # Delete the duplicate
                    bpy.ops.object.delete()
                else:
                    print("No mesh child found for the armature.")
            # else: print("where is the hand")

            new_image_paths.append(target_base_path)

def compute_6d_pose_in_camera_coords(extrinsic, obj):
    # Get the object's rotation matrix
    obj_matrix_rotation=obj.matrix_world
    obj_euler_rotation = obj_matrix_rotation.to_euler()

    obj_euler_rotation[2]+= math.radians(90)
    obj_rotation_matrix=transforms3d.euler.euler2mat(obj_euler_rotation[0],obj_euler_rotation[1],obj_euler_rotation[2])
    location = obj.location
    t_obj = np.array([-1*location.y,location.x , location.z])

    object_pose_world= np.column_stack((obj_rotation_matrix, t_obj))
    object_pose_homogeneous = np.vstack((object_pose_world, [0, 0, 0, 1]))

    # modify this later
    camera_pose_world=np.zeros([4,4])
    camera_pose_world[0,:]=extrinsic[1,:]
    camera_pose_world[1,:]=extrinsic[0,:]
    camera_pose_world[2,:]=extrinsic[2,:]
    camera_pose_world[0,0]=-1*camera_pose_world[0,0]
    camera_pose_world[1,1]=-1*camera_pose_world[1,1]
    camera_pose_world[1,2]=-1*camera_pose_world[1,2]
    camera_pose_world[0,3]=-1*camera_pose_world[0,3]
    camera_pose_world[2,1]=-1*camera_pose_world[2,1]
    camera_pose_world[2,2]=-1*camera_pose_world[2,2]
    camera_pose_world[3,:]=[0,0,0,1]
    
    # camera wTc rename later
    camera_pose_world_inv = np.linalg.inv(camera_pose_world)
    pose = np.dot(camera_pose_world_inv, object_pose_homogeneous)
    return pose[:-1, :]

def get_3d_hand_pose(extrinsic, hand):
    bones_names2 = [
    "thumb_meta.L",
    "thumb_prox.L",
    "thumb_dist.L",
    "index_meta.L",
    "index_prox.L",
    "index_inter.L",
    "index_dist.L",
    "middle_meta.L",
    "middle_prox.L",
    "middle_inter.L",
    "middle_dist.L",
    "ring_meta.L",
    "ring_prox.L",
    "ring_inter.L",
    "ring_dist.L",
    "pinkie_meta.L",
    "pinkie_prox.L",
    "pinkie_inter.L",
    "pinkie_dist.L"
    ]
    bones_names1=[
        "wrist.L",
        "thumb_meta.L"
        ]
    world_tail_position=[]
    sz1=len(bones_names1)
    sz2=len(bones_names2)
    sz=sz1+sz2
    world_tail_position=np.zeros((sz,3))
    joint_poses=np.zeros((sz,3))
    i=0

    # Get and print world positions of the tail of the bones (end of the bones)
    for bone_name in bones_names1:
        bone = hand.pose.bones[bone_name].head
        world_tail_position[i,:] = hand.matrix_world @ bone
        i=i+1
    for bone_name in bones_names2:
        bone = hand.pose.bones[bone_name].tail
        world_tail_position[i,:] = hand.matrix_world @ bone
        i=i+1

    ## transform to camera coordinate system
    # transform to the same world coordinate system first
    world_tail_position1=world_tail_position
    # do we need to add 90 degree? yes
    world_tail_position1[:,1]=world_tail_position1[:,1]*-1
    world_tail_position1[:,[0,1]]=world_tail_position1[:,[1,0]]

    # calculate the position under camera coordinate system
    # transform to real R|t matrix first
    # just a workaround, modify this later
    camera_pose_world=np.zeros([4,4])
    camera_pose_world[0,:]=extrinsic[1,:]
    camera_pose_world[1,:]=extrinsic[0,:]
    camera_pose_world[2,:]=extrinsic[2,:]
    camera_pose_world[0,0]=-1*camera_pose_world[0,0]
    camera_pose_world[1,1]=-1*camera_pose_world[1,1]
    camera_pose_world[1,2]=-1*camera_pose_world[1,2]
    camera_pose_world[0,3]=-1*camera_pose_world[0,3]
    camera_pose_world[2,1]=-1*camera_pose_world[2,1]
    camera_pose_world[2,2]=-1*camera_pose_world[2,2]
    camera_pose_world[3,:]=[0,0,0,1]

    camera_pose_world_inv = np.linalg.inv(camera_pose_world)

    # no rotation, just calculate position
    # introduce a fake R matrix can be integrate with mesh export later 
    R_obj=np.array([[0,-1,0],[1,0,0],[0,0,1]])
    for i in range (sz):
        
        t_obj=world_tail_position1[i,:]
        joint_pose_matrix_world=np.column_stack((R_obj,t_obj))
        joint_pose_homogeneous = np.vstack((joint_pose_matrix_world, [0, 0, 0, 1]))
        joint_pose_camera_matrix = np.dot(camera_pose_world_inv, joint_pose_homogeneous)
        joint_poses[i]=joint_pose_camera_matrix[:-1,3]
    joint_poses=np.expand_dims(joint_poses,axis=0)
    return joint_poses

    ## project 3d hand pose to 2d
def get_2d_hand_pose(intrinsic,hand_pose_3d):
    hand_pose_2d=np.zeros([1,21,2])
    hand_pose_3d=np.squeeze(hand_pose_3d)
    for i in range(21):
        p=hand_pose_3d[i,:]
        p_homogeneous=np.matmul(intrinsic,p)
        hand_pose_2d[0,i,:]=[p_homogeneous[0]/p_homogeneous[2],p_homogeneous[1]/p_homogeneous[2]]
    return hand_pose_2d
