"""
Copyright (C) 2024 Chengyan Zhang

This file is part of blender-hoisynth, you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.

You should have received a copy of the GNU General Public License along with blender-hoisynth. If not, see <http://www.gnu.org/licenses/>.
"""

import argparse
import numpy as np
import os
import glob
import yaml

def python_tuple_constructor(loader, node):
    return tuple(loader.construct_sequence(node))

yaml.Loader.add_constructor(u'tag:yaml.org,2002:python/tuple', python_tuple_constructor)

def find_extrinsics_by_index(subject_num, base_parent_directory):
    all_extrinsics = sorted(glob.glob(os.path.join(base_parent_directory, "calibration/extrinsics_*")))
    if 0 <= subject_num-1 < len(all_extrinsics):
        return all_extrinsics[subject_num-1]
    else:
        return None

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--DexYCB_dir', type=str, default='/home/DexYCB')
    parser.add_argument('--output_dir', type=str, default='/home/blender-hoisynth/assets/initial_positions')
    return parser.parse_args()

args = parse_args()
base_parent_directory = args.DexYCB_dir
output_directory = args.output_dir
subject_folders = sorted(glob.glob(os.path.join(base_parent_directory, "*-subject-*")), key=lambda x: int(x.split('-')[-1]))

for subject_folder in subject_folders:
    subject_date = subject_folder.split('/')[-1].split('-')[0] 
    subject_num = subject_folder.split('/')[-1].split('-')[-1]
    base_directory = os.path.join(base_parent_directory, f"{subject_date}-subject-{subject_num}")
    

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    npz_file_paths = glob.glob(os.path.join(base_directory, "*/840412060917/labels_000000.npz"))
    sorted_npz_file_paths = sorted(npz_file_paths, key=lambda x: int(x.split(os.sep)[-3].split('_')[-1]))

    extrinsics_dir = find_extrinsics_by_index(int(subject_num), base_parent_directory)
    if extrinsics_dir is None:
        print(f"No extrinsics directory found for {subject_folder}. Skipping.")
        continue
    extrinsics_path = os.path.join(extrinsics_dir, 'extrinsics.yml')
    print(base_directory,output_directory,extrinsics_path)

    with open(extrinsics_path, 'r') as file:
        extrinsics = yaml.load(file, Loader=yaml.Loader)

    apriltag = np.array(extrinsics['extrinsics']['apriltag']).reshape((3, 4))
    cTw = np.vstack([apriltag, [0, 0, 0, 1]]) 


    for idx, npz_file_path in enumerate(sorted_npz_file_paths):

        
        yaml_file_path = os.path.join(os.path.dirname(os.path.dirname(npz_file_path)), 'meta.yml')
        if not os.path.exists(yaml_file_path):
            print(f"Warning: Corresponding yaml file not found for {npz_file_path}")
            continue

        with open(yaml_file_path, 'r') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
            ycb_ids = yaml_data.get('ycb_ids', [])

        with np.load(npz_file_path) as data:
            # Extract pose_y data
            pose_y = data['pose_y']
            pose_y_new=np.zeros(pose_y.shape)
            for i, index in enumerate(ycb_ids):
                pose_y_homo = np.vstack([pose_y[i], [0, 0, 0, 1]])
                wTo=np.dot(np.linalg.inv(cTw),pose_y_homo)
                pose_y_new[i,:,:]=wTo[:3,:]
            new_file_name = f"{npz_file_path.split('/')[-3]}.npz"
            new_file_path = os.path.join(output_directory, new_file_name)
            np.savez_compressed(new_file_path, pose_y=pose_y_new, ycb_ids=ycb_ids)
    print(f"Process completed for subject-{subject_num}.")

print("All subjects processed.")