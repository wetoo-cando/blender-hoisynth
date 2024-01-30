"""
Copyright (C) 2024 Chengyan Zhang

Based on https://github.com/facebookresearch/ContactPose/blob/a0920d88737418bf840b2445e01ea67adbc546c1/utilities/mano_fitting.py#L42
"""

import argparse
import numpy as np
import torch
import sys
import yaml
import cv2
import matplotlib.pyplot as plt
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import render_config_test as render_config
import torch
from manopth.manolayer import ManoLayer
from manopth import demo
from open3d import pipelines

from torchmin import minimize

import json
import transforms3d as t3d
import transforms3d.quaternions as txq
import pickle
from open3d import io as o3dio
from open3d import visualization as o3dv
from open3d import utility as o3du
from open3d import geometry as o3dg
from open3d import pipelines
osp = os.path
o3dr = pipelines.registration
print("check gpu information:",torch.cuda.device_count(),torch.cuda.current_device(),torch.cuda.get_device_name(0))
torch.cuda.set_device(0)


index_to_name = {
    1: ['master_chef_can'],
    2: ['cracker_box'],
    3: ['sugar_box'],
    4: ['tomato_soup_can'],
    5: ['mustard_bottle'],
    6: ['tuna_fish_can'],
    7: ['pudding_box'],
    8: ['gelatin_box'],
    9: ['potted_meat_can'],
    10: ['banana'],
    11: ['pitcher_base'],
    12: ['bleach_cleanser'],
    13: ['bowl'],
    14: ['mug'],
    15: ['power_drill'],
    16: ['wood_block'],
    17: ['scissors'],
    18: ['large_marker'],
    19: ['extra_large_clamp'],
    20: ['extra_large_clamp'],
    21: ['foam_brick']
}

def get_palm_joints(p, n_joints_per_finger=4):

  # get the 6 palm joints (root + base of all 5 fingers)
  idx = [0]
  for fidx in range(5):
    idx.append(1 + fidx*n_joints_per_finger)
  return p[:,idx,:]

def register_pcs(src, tgt, verbose=True):

  assert(len(src) == len(tgt))
  ps = o3dg.PointCloud()
  ps.points = o3du.Vector3dVector(src)
  pt = o3dg.PointCloud()
  pt.points = o3du.Vector3dVector(tgt)
  c = [[i, i] for i in range(len(src))]
  c = o3du.Vector2iVector(c)
  r = o3dr.TransformationEstimationPointToPoint()
  r.with_scaling = False
  if verbose:
    print('Rigid registration RMSE (before) = {:f}'.
          format(r.compute_rmse(ps, pt, c)))
  tTs = r.compute_transformation(ps, pt, c)
  pst = ps.transform(tTs)
  if verbose:
    print('Rigid registration RMSE (after) = {:f}'.
          format(r.compute_rmse(pst, pt, c)))
  return tTs

def fit_joints(input_joints,hand_name,n_pose_params,betas=None, shape_sigma=10.0):
    mano_params = []
    if hand_name=="LEFT":
      hand_idx=0
    elif hand_name=="RIGHT":
      hand_idx=1
    else: hand_idx==None
    cp_joints=input_joints
    cp_joints=torch.unsqueeze(torch.tensor(np.array(cp_joints)),dim=0).float()*1000
    cp_joints=torch.squeeze(cp_joints,dim=0)
    m= ManoLayer(mano_root='examples/rendering/manopth/mano/models', use_pca=True, ncomps=45, flat_hand_mean=False)
    

    if betas is not None:
      betas=torch.unsqueeze(torch.tensor(np.array(betas['betas'])),0).float()
      global_rotation=torch.rand(1,3)
      global_translation=torch.rand(1,3)
      local_pose=torch.zeros(1,n_pose_params)
      mano_params=torch.cat((global_rotation,local_pose,global_translation),dim=1).float()
      verts,mano_joints = m(th_betas=betas,
                                th_pose_coeffs=mano_params[:,:n_pose_params+3],
                                th_trans=global_translation)
      mano_joints_np = np.array(mano_joints)
      

      # align palm
      cp_palm = get_palm_joints(np.asarray(cp_joints))
      cp_palm=np.squeeze(cp_palm)
      mano_palm = get_palm_joints(np.asarray(mano_joints_np))
      mano_palm=np.squeeze(mano_palm)

      mTc = register_pcs(cp_palm, mano_palm)


      cp_joints = np.dot(mTc, np.vstack((np.squeeze(np.array(cp_joints.T)), np.ones(21))))
      
      cp_joints = cp_joints[:3].T
      cp_joints = torch.tensor(cp_joints).float()

      def objective(x):
          betas_con=betas 
          transl=x[:,48:]
          verts,mano_joints = m(th_betas=betas_con,
                                th_pose_coeffs=x[:,:n_pose_params+3],
                                th_trans=transl)
          mano_joints[0,8,:]=verts[0,309,:]
          mano_joints=mano_joints.float()
          loss = torch.nn.functional.mse_loss(input=mano_joints[0,:,:], target=cp_joints)
          loss=loss.float()
          return loss
      res = minimize(fun=objective, x0=mano_params, method='l-bfgs',disp=1,options={'gtol': 1e-9})
    else:
      betas_new=torch.zeros(1,10).float()
      global_rotation=torch.rand(1,3)
      global_translation=torch.rand(1,3)
      local_pose=torch.zeros(1,n_pose_params)
      mano_params=torch.cat((global_rotation,local_pose,global_translation),dim=1).float()
      verts,mano_joints = m(th_betas=betas_new,
                                th_pose_coeffs=mano_params[:,:n_pose_params+3],
                                th_trans=global_translation)
      mano_joints_np = np.array(mano_joints)

      # align palm
      cp_palm = get_palm_joints(np.asarray(cp_joints))
      cp_palm=np.squeeze(cp_palm)
      mano_palm = get_palm_joints(np.asarray(mano_joints_np))
      mano_palm=np.squeeze(mano_palm)

      mTc = register_pcs(cp_palm, mano_palm)

      mixed_params=torch.cat((betas_new,global_rotation,local_pose,global_translation),dim=1).float()

      cp_joints = np.dot(mTc, np.vstack((np.squeeze(np.array(cp_joints.T)), np.ones(21))))
      cp_joints = cp_joints[:3].T
      cp_joints = torch.tensor(cp_joints).float()

      def objective(x):
          mixed_params
          betas_con=x[:,:10] 
          transl=x[:,58:]
          verts,mano_joints = m(th_betas=betas_con,
                                th_pose_coeffs=x[:,10:n_pose_params+13],
                                th_trans=transl)
          mano_joints[0,8,:]=verts[0,309,:]
          mano_joints=mano_joints.float()
          # print("sizes:",mano_joints.shape,cp_joints.shape)
          loss = torch.nn.functional.mse_loss(input=mano_joints[0,:,:], target=cp_joints)
          loss=loss.float()
          return loss
      res = minimize(fun=objective, x0=mixed_params, method='l-bfgs',disp=1,options={'gtol': 1e-9})
    return res.x

def fit_global(input_joints,hand_name,n_pose_params,local_pose,betas=None, shape_sigma=10.0):
    mano_params = []
    if hand_name=="LEFT":
      hand_idx=0
    elif hand_name=="RIGHT":
      hand_idx=1
    else: hand_idx==None
    cp_joints=input_joints
    cp_joints=torch.unsqueeze(torch.tensor(np.array(cp_joints)),dim=0).float()*1000
    m= ManoLayer(mano_root='examples/rendering/manopth/mano/models', use_pca=True, ncomps=45, flat_hand_mean=False)
    betas=torch.unsqueeze(torch.tensor(np.array(betas['betas'])),0).float()
    global_params=torch.rand(1,6)
    global_rotation=global_params[:,:3]
    global_translation=global_params[:,3:]
    mano_params=torch.cat((global_rotation,local_pose,global_translation),dim=1).float()
    
    cp_joints=torch.squeeze(cp_joints,dim=0)

    cp_joints = torch.tensor(cp_joints).float()

    def objective(x):
        betas_con=betas
        global_rot=x[:,:3]
        pose_coeff=torch.cat((global_rot,local_pose),dim=1).float()
        transl=x[:,3:]
        verts,mano_joints = m(th_betas=betas_con,
                              th_pose_coeffs=pose_coeff,
                              th_trans=transl)
        mano_joints[0,8,:]=verts[0,309,:]
        mano_joints=mano_joints.float()
        #print("sizes:",mano_joints.shape,cp_joints.shape)
        loss = torch.nn.functional.mse_loss(input=mano_joints[0,:,:], target=cp_joints)
        loss=loss.float()
        return loss
    res = minimize(fun=objective, x0=global_params, method='l-bfgs',disp=1,options={'gtol': 1e-9})
    return res.x

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--blend_dir", type=str, default='/home/blendfiles')
    parser.add_argument("--callibration_dir", type=str, default='/home/blender-hoisynth/assets/calibration')
    parser.add_argument("--pose_dir", type=str, default='/home/blender-hoisynth/assets/initial_positions')
    parser.add_argument('--output_dir', type=str, default='/home/blender-hoisynth/BlenderProc/output')
    parser.add_argument('--mano_dir', type=str, default='mano_20200820_133405_subject-03_right')    
    parser.add_argument('--Subject_id', type=str, default='test')
    return parser.parse_args()

args=parse_args()
blend_folder=args.blend_dir

for i in range (len(render_config.config_instance.blendfiles)):
  render_config.config_instance.chosen_blendfile= str(i)
  blend_path=os.path.join(blend_folder,render_config.config_instance.blendfilename)

  grasp_obj=render_config.config_instance.mesh_export_order
  grasp_index = next((i for i, name in index_to_name.items() if name == grasp_obj), None)


  blend_file="_".join(blend_path.split('/')[-1].split('.')[0].split('_')[:2])
  root_path=os.path.join(args.output_dir,args.Subject_id,blend_file)

  mano_path=os.path.join(args.callibration_dir,args.mano_dir)

  mano_file=os.path.join(mano_path,f"mano.yml")

  if not os.path.exists(mano_path):
      print("no calibration data")
      os.makedirs(mano_path)
  pca_num=45
  # List of directories
  dirs = ["836212060125", "839512060362", "840412060917", "841412060263", "932122060857", "932122060861","932122061900", "932122062010"]
  # Check if the file exists
  for dir in dirs:
      num=len([f for f in os.listdir(os.path.join(root_path,dir)) if os.path.isfile(os.path.join(root_path,dir, f))])
      for i in range(num):
          file_name = os.path.join(root_path, dir, f"labels_{i:06d}.npz")
          file_name2=file_name
          if os.path.exists(file_name):
                  # Load the npz file
              with np.load(file_name) as data:
                joint_3d=data['joint_3d']
                input_joint=torch.tensor(joint_3d).float()
                pose_y=data['pose_y']
                joint_2d=data['joint_2d']
                seg=data['seg'].astype(np.uint8)
              if os.path.exists(mano_file):
                  with open(mano_file, 'r') as file:
                     betas = yaml.safe_load(file)
                  # print((betas['betas']))
                  mano_params=fit_joints(input_joint,'RIGHT',pca_num,betas)
                  local_pose=mano_params[:,3:48]
                  global_params=fit_global(input_joint,'RIGHT',pca_num,local_pose,betas)
                  #print(global_params)
                  mano_params[:,48:]=global_params[:,3:]
                  mano_params[:,:3]=global_params[:,:3]

                  with open(file_name2,'wb') as file:
                    np.savez_compressed(file,seg=seg, pose_y=pose_y,pose_m=mano_params,joint_3d=joint_3d,joint_2d=joint_2d)
                    print(f"Processed and updated {file_name2}")
              else:
                  mixed_params=fit_joints(input_joint,'RIGHT',pca_num)
                  mano_params=mixed_params[:,10:]
                  print("first mano_params:",mano_params.shape)
                  betas = {'betas': mixed_params[0,:10].tolist()}
                  local_pose=mano_params[:,3:48]
                  global_params=fit_global(input_joint,'RIGHT',pca_num,local_pose,betas)
                  #print(global_params) 
                  mano_params[:,48:]=global_params[:,3:]
                  mano_params[:,:3]=global_params[:,:3]
                  with open(file_name2,'wb') as file:
                    np.savez_compressed(file,seg=seg, pose_y=pose_y,pose_m=mano_params,joint_3d=joint_3d,joint_2d=joint_2d)
                    print(f"Processed and updated {file_name2}")
                  with open(mano_file, 'w') as file:
                      yaml.dump(betas, file)


  ## generate sequence pose and yaml file
  pose_m_list = []
  pose_y_list = []

  cam_path=os.path.join(root_path, f'840412060917')
  labels = sorted(os.listdir(cam_path))
  for label in labels:
      if label.endswith('.npz'):
        with np.load(os.path.join(cam_path,label)) as data:
          pose_m = data['pose_m']
          pose_y = data['pose_y']
          new_pose_y = []
          for j in range(pose_y.shape[0]):
              rot_mat = pose_y[j, :, :3]
              trans_vec = pose_y[j, :, 3]
              quaternion = t3d.quaternions.mat2quat(rot_mat)
              quaternion=quaternion[[1, 2, 3, 0]]
              combined = np.concatenate((quaternion, trans_vec))
              new_pose_y.append(combined)
          
        pose_m_list.append(pose_m.reshape(1, 1, -1))
        pose_y_list.append(np.array(new_pose_y).reshape(1,len(new_pose_y), -1))

  pose_m_array = np.concatenate(pose_m_list, axis=0)
  pose_y_array = np.concatenate(pose_y_list, axis=0).astype(np.float32)

  sequence_pose_file=os.path.join(root_path,'pose.npz')
  sequence_meta_file=os.path.join(root_path,'meta.yml')
  with open(sequence_pose_file,'wb') as file:
    np.savez_compressed(file, pose_m=pose_m_array, pose_y=pose_y_array)
  with np.load(os.path.join(args.pose_dir,blend_file+'.npz')) as data:
     allowed_category_ids = data['ycb_ids'].tolist()

  try:
    index_in_list = allowed_category_ids.index(grasp_index)
  except ValueError:
    print(f"{grasp_index} is not in the list.")

  meta={
        "serials": [
          '836212060125',
          '839512060362',
          '840412060917',
          '841412060263',
          '932122060857',
          '932122060861',
          '932122061900',
          '932122062010'
      ],
      "num_frames":pose_y_array.shape[0],
      "extrinsics": '20201022_091549',
      "ycb_ids":allowed_category_ids,
      "ycb_grasp_ind": index_in_list,
      "mano_sides": ['right'],
      "mano_calib": ["_".join(args.mano_dir.split("_")[1:])]
  }
  with open(sequence_meta_file, "w") as file:
      yaml.dump(meta, file, default_flow_style=False, sort_keys=False)
