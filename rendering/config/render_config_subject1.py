import numpy as np
turn_on_coco_bop_annotations = True
ignore_obj_by_name = ['decimated', 'workspace', 'omni', 'Leap_Motion', 'next_joint', 'prev_joint', 
'anchor',
'L1.004',
'L1.001', 'L1.005',
'fingertip_sensor', 'collision_sensor',
'Cube.020',
'subdesk',
'Camera',
'mug.001',
"Asian_Male_20's_Hand_Neutral_SubD_L1.010",
"Asian_Male_20's_Hand_Neutral_SubD_L1.004",
"left_orig_hand_asian_002_scale_x70pc_y80pc_z90pc",
"Asian_Male_20's_Hand_Neutral_SubD_L1.001",
"Asian_Male_20's_Hand_Neutral_SubD_L1.002",
"Asian_Male_20's_Hand_Neutral_SubD_L1.003",
"Asian_Male_20's_Hand_Neutral_SubD_L1.004",
"Asian_Male_20's_Hand_Neutral_SubD_L1.006",
"Asian_Male_20's_Hand_Neutral_SubD_L1.007",
"Asian_Male_20's_Hand_Neutral_SubD_L1.008",
"Asian_Male_20's_Hand_Neutral_SubD_L1.011",
"Asian_Male_20's_Hand_Neutral_SubD_L1.012",
"Asian_Male_20's_Hand_Neutral_SubD_L1.013",
"Asian_Male_20's_Hand_Neutral_SubD_L1.014",
"Asian_Male_20's_Hand_Neutral_SubD_L1.015",
"Asian_Male_20's_Hand_Neutral_SubD_L1.016",
"Asian_Male_20's_Hand_Neutral_SubD_L1.017",
"Asian_Male_20's_Hand_Neutral_SubD_L1.018",
"Asian_Male_20's_Hand_Neutral_SubD_L1.019"

]
_ignore_obj_ycb = ['strawberry', 'apple', 'lemon', 'peach', 'pear', 'orange', 'plum', 'windex', 'softball',
                   'sponge', 'skillet', 'plate', 'fork', 'spoon', 'knife', 'spatula', 'wrench', 'screwdriver','hammer', 'baseball', 'hole_peg', 'airplane', 'rubiks']

_ignore_obj_ycb2=[]
_ignore_obj_peter_rabbit = ['Benjamin', 'lili', 'peter']
_ignore_obj_toys = ['Drache', 'cow', 'muli', 'tonie']
ignore_obj_by_name.extend(_ignore_obj_ycb)
ignore_obj_by_name.extend(_ignore_obj_peter_rabbit)
ignore_obj_by_name.extend(_ignore_obj_toys)
ignore_obj_by_name.extend(_ignore_obj_ycb2)

# Camera intrinsics
'''
default_camera_intrinsics = [[621.7969970703125, 0.0, 302.4136962890625],
                            [0.0, 621.4028930664062, 236.88433837890625],
                            [0.0, 0.0, 1.0]]
'''
image_width = 640
image_height= 480
use_dexycb_intrinsics = True

camera_matrices = {}
'''
camera_matrices['test'] = {}
camera_matrices['test']['extrinsic'] = np.array(((0,-1,0,0),(-1,0,0,0),(0,0,-1,-5),(0.0, 0.0, 0.0, 1.0)))
camera_matrices['test']['intrinsic'] = [[616.640869140625, 0.0, 308.548095703125],[0.0, 616.2581787109375,248.52310180664062],[0.0, 0.0, 1.0]]
'''

# cam 0 
camera_matrices['836212060125'] = {}
camera_matrices['836212060125']['extrinsic'] = np.array(((-7.807548046112060547e-01,-9.459716826677322388e-02,-6.176353096961975098e-01,-2.112371325492858887e-01),(-6.244967579841613770e-01,1.507883518934249878e-01,7.663332819938659668e-01,1.487655192613601685e-01),(2.063930407166481018e-02,9.840295910835266113e-01,-1.768044680356979370e-01,8.543297648429870605e-02),(0.0, 0.0, 0.0, 1.0)))
camera_matrices['836212060125']['intrinsic'] = [[616.640869140625, 0.0, 308.548095703125],[0.0, 616.2581787109375,248.52310180664062],[0.0, 0.0, 1.0]]

# cam 1
camera_matrices['839512060362'] = {}
camera_matrices['839512060362']['extrinsic'] = np.array(((7.358905673027038574e-01,-1.187089309096336365e-01,-6.666129827499389648e-01,-2.474758028984069824e-01),(-6.769675016403198242e-01,-1.484771519899368286e-01,-7.208809852600097656e-01,-1.275655031204223633e+00),(-1.340191159397363663e-02, 9.817651510238647461e-01, -1.896249502897262573e-01,9.470409899950027466e-02),(0.0, 0.0, 0.0, 1.0)))
camera_matrices['839512060362']['intrinsic'] = [[616.24951171875, 0.0, 321.6138916015625],[0.0, 615.8766479492188,244.82809448242188],[0.0, 0.0, 1.0]]


# cam 2 
camera_matrices['840412060917'] = {}
camera_matrices['840412060917']['extrinsic'] = np.array(((5.872488021850585938e-01,-4.956215322017669678e-01,6.399203538894653320e-01,8.334187865257263184e-01),(8.092896938323974609e-01,3.461039662361145020e-01,-4.746180772781372070e-01,-1.091962814331054688e+00),(1.375195011496543884e-02,7.965998649597167969e-01,6.043505072593688965e-01,6.869019865989685059e-01),(0.0, 0.0, 0.0, 1.0)))
camera_matrices['840412060917']['intrinsic'] = [[621.7969970703125, 0.0, 302.4136962890625],[0.0, 621.4028930664062,236.88433837890625],[0.0, 0.0, 1.0]]


# cam 3
camera_matrices['841412060263'] = {}
camera_matrices['841412060263']['extrinsic'] = np.array(((-4.989651143550872803e-01,-4.952136576175689697e-01,7.111942172050476074e-01,8.875430822372436523e-01),(8.652460575103759766e-01,-3.308981955051422119e-01,3.766375184059143066e-01,-1.971387416124343872e-01),(4.881685227155685425e-02,8.032869100570678711e-01,5.935882925987243652e-01,6.923591494560241699e-01),(0.0, 0.0, 0.0, 1.0)))
camera_matrices['841412060263']['intrinsic'] = [[615.357421875, 0.0, 322.17333984375],[0.0, 615.207275390625,238.35340881347656],[0.0, 0.0, 1.0]]

# cam 4
camera_matrices['932122060857'] = {}
camera_matrices['932122060857']['extrinsic'] = np.array(((-9.993125200271606445e-01,5.349526763893663883e-04,-3.706893324851989746e-02,2.995659708976745605e-01),(-2.214247174561023712e-02,-8.105701804161071777e-01,5.852229595184326172e-01,-2.934963703155517578e-01),(-2.973381429910659790e-02,5.856413841247558594e-01,8.100247383117675781e-01,8.880697488784790039e-01),(0.0, 0.0, 0.0, 1.0)))
camera_matrices['932122060857']['intrinsic'] = [[612.2747192382812, 0.0, 313.3760681152344],[0.0, 610.9385986328125,238.7041015625],[0.0, 0.0, 1.0]]

# cam 5 
camera_matrices['932122060861'] = {}
camera_matrices['932122060861']['extrinsic'] = np.array(((9.989122152328491211e-01,-2.285546250641345978e-02,-4.064434021711349487e-02,2.173504829406738281e-01),(-5.516730248928070068e-03,8.075912594795227051e-01,-5.897167921066284180e-01,-9.146782159805297852e-01),(4.630221426486968994e-02,5.892995595932006836e-01,8.065867424011230469e-01,8.951443433761596680e-01),(0.0, 0.0, 0.0, 1.0)))
camera_matrices['932122060861']['intrinsic'] = [[613.0762329101562, 0.0, 313.0279846191406],[0.0, 611.9989624023438,245.00865173339844],[0.0, 0.0, 1.0]]

# cam 6
camera_matrices['932122061900'] = {}
camera_matrices['932122061900']['extrinsic'] = np.array(((7.473163008689880371e-01,2.987732589244842529e-01,-5.935088992118835449e-01,-2.696463763713836670e-01),(-6.565078496932983398e-01,4.698467850685119629e-01,-5.901199579238891602e-01,-1.084081649780273438e+00),(1.025461852550506592e-01,8.306494951248168945e-01,5.472711324691772461e-01,6.688058972358703613e-01),(0.0, 0.0, 0.0, 1.0)))
camera_matrices['932122061900']['intrinsic'] = [[615.69775390625, 0.0, 315.19110107421875],[0.0, 614.3549194335938,242.0313262939453],[0.0, 0.0, 1.0]]

# cam 7
camera_matrices['932122062010'] = {}
camera_matrices['932122062010']['extrinsic'] = np.array(((-7.415711879730224609e-01,3.086528480052947998e-01,-5.956555604934692383e-01,-3.177022933959960938e-01),(-6.680071949958801270e-01,-4.217181205749511719e-01,6.131233572959899902e-01,-5.829757824540138245e-02),(-6.195644289255142212e-02,8.525768518447875977e-01,5.189163088798522949e-01,6.694388389587402344e-01),(0.0, 0.0, 0.0, 1.0)))
camera_matrices['932122062010']['intrinsic'] = [[615.7017822265625, 0.0, 321.1631774902344],[0.0, 614.4563598632812,239.0236053466797],[0.0, 0.0, 1.0]]



class BlenderConfig:
    blendfiles = {
    '0': '20200709_141754.blend',
    '1': '20200709_141841.blend',
    '2': '20200709_142123.blend',
    '3': '20200709_142211.blend',
    '4': '20200709_142240.blend',
    '5': '20200709_142517.blend',
    '6': '20200709_142553.blend',
    '7': '20200709_142802.blend',
    '8': '20200709_142853.blend',
    '9': '20200709_142926.blend',
    '10': '20200709_143125.blend',
    '11': '20200709_143211.blend',
    '12': '20200709_143257.blend',
    '13': '20200709_143626.blend',
    '14': '20200709_143703.blend',
    '15': '20200709_143907.blend',
    '16': '20200709_143957.blend',
    '17': '20200709_144056.blend',
    '18': '20200709_144313.blend',
    '19': '20200709_144357.blend',
    '20': '20200709_144429.blend',
    '21': '20200709_144814.blend',
    '22': '20200709_144854.blend',
    '23': '20200709_145401.blend',
    '24': '20200709_145446.blend',
    '25': '20200709_145837.blend',
    '26': '20200709_145915.blend',
    '27': '20200709_150144.blend',
    '28': '20200709_150243.blend',
    '29': '20200709_150326.blend',
    '30': '20200709_150613.blend',
    '31': '20200709_150654.blend',
    '32': '20200709_150906.blend',
    '33': '20200709_150949.blend',
    '34': '20200709_151032.blend',
    '35': '20200709_151335.blend',
    '36': '20200709_151415.blend',
    '37': '20200709_151724.blend',
    '38': '20200709_151757.blend',
    '39': '20200709_151948.blend',
    '40': '20200709_152056.blend',
    '41': '20200709_152143.blend',
    '42': '20200709_152506.blend',
    '43': '20200709_152541.blend',
    '44': '20200709_152843.blend',
    '45': '20200709_152930.blend',
    '46': '20200709_153148.blend',
    '47': '20200709_153241.blend',
    '48': '20200709_153322.blend',
    '49': '20200709_153548.blend',
                }


    frame_settings={
        blendfiles['0']:{
            'frame_start'  : [30],
            'num_frames'   : [126-30],
            'step'         : 300
                        },
        blendfiles['1'] :{
            'frame_start'  : [36],
            'num_frames'   : [140-36],
            'step'         : 300
                        },
        blendfiles['2'] :{
            'frame_start'  : [36],
            'num_frames'   : [169-36],
            'step'         : 300
                        },
            blendfiles['3'] :{
            'frame_start'  : [36],
            'num_frames'   : [129-36],
            'step'         : 300
                        },
        blendfiles['4']:{
            'frame_start'  : [36],
            'num_frames'   : [181-36],
            'step'         : 300
                        },
        blendfiles['5'] :{
            'frame_start'  : [36],
            'num_frames'   : [193-36],
            'step'         : 300
                        },
        blendfiles['6'] :{
            'frame_start'  : [36],
            'num_frames'   : [164-36],
            'step'         : 300
                        },
        blendfiles['7'] :{
            'frame_start'  : [36],
            'num_frames'   : [153-36],
            'step'         : 300
                        },
        blendfiles['8']:{
            'frame_start'  : [36],
            'num_frames'   : [129-36],
            'step'         : 300
                        },
        blendfiles['9'] :{
            'frame_start'  : [36],
            'num_frames'   : [181-36],
            'step'         : 300
                        },
        blendfiles['10'] :{
            'frame_start'  : [36],
            'num_frames'   : [183-36],
            'step'         : 300
                        },
        blendfiles['11'] :{
            'frame_start'  : [36],
            'num_frames'   : [164-36],
            'step'         : 300
                        },
        blendfiles['12']:{
            'frame_start'  : [36],
            'num_frames'   : [191-36],
            'step'         : 300
                        },
        blendfiles['13'] :{
            'frame_start'  : [36],
            'num_frames'   : [186-36],
            'step'         : 300
                        },
        blendfiles['14'] :{
            'frame_start'  : [36],
            'num_frames'   : [173-36],
            'step'         : 300
                        },
        blendfiles['15'] :{
            'frame_start'  : [36],
            'num_frames'   : [165-36],
            'step'         : 300
                        },
        blendfiles['16']:{
            'frame_start'  : [36],
            'num_frames'   : [191-36],
            'step'         : 300
                        },
        blendfiles['17'] :{
            'frame_start'  : [36],
            'num_frames'   : [142-36],
            'step'         : 300
                        },
        blendfiles['18'] :{
            'frame_start'  : [36],
            'num_frames'   : [171-36],
            'step'         : 300
                        },
        blendfiles['19'] :{
            'frame_start'  : [36],
            'num_frames'   : [172-36],
            'step'         : 300
                        },
        blendfiles['20']:{
            'frame_start'  : [36],
            'num_frames'   : [220-36],
            'step'         : 300
                        },
        blendfiles['21'] :{
            'frame_start'  : [36],
            'num_frames'   : [263-36],
            'step'         : 300
                        },
        blendfiles['22'] :{
            'frame_start'  : [36],
            'num_frames'   : [212-36],
            'step'         : 300
                        },
        blendfiles['23'] :{
            'frame_start'  : [36],
            'num_frames'   : [173-36],
            'step'         : 300
                        },
        blendfiles['24']:{
            'frame_start'  : [36],
            'num_frames'   : [219-36],
            'step'         : 300
                        },
        blendfiles['25'] :{
            'frame_start'  : [36],
            'num_frames'   : [212-36],
            'step'         : 300
                        },
        blendfiles['26'] :{
            'frame_start'  : [36],
            'num_frames'   : [262-36],
            'step'         : 300
                        },
        blendfiles['27'] :{
            'frame_start'  : [36],
            'num_frames'   : [241-36],
            'step'         : 300
                        },
        blendfiles['28']:{
            'frame_start'  : [36],
            'num_frames'   : [181-36],
            'step'         : 300
                        },
        blendfiles['29'] :{
            'frame_start'  : [36],
            'num_frames'   : [236-36],
            'step'         : 300
                        },
        blendfiles['30'] :{
            'frame_start'  : [36],
            'num_frames'   : [242-36],
            'step'         : 300
                        },
        blendfiles['31'] :{
            'frame_start'  : [36],
            'num_frames'   : [248-36],
            'step'         : 300
                        },
        blendfiles['32']:{
            'frame_start'  : [36],
            'num_frames'   : [250-36],
            'step'         : 300
                        },
        blendfiles['33'] :{
            'frame_start'  : [36],
            'num_frames'   : [280-36],
            'step'         : 300
                        },
        blendfiles['34'] :{
            'frame_start'  : [36],
            'num_frames'   : [204-36],
            'step'         : 300
                        },
        blendfiles['35'] :{
            'frame_start'  : [36],
            'num_frames'   : [260-36],
            'step'         : 300
                        },
        blendfiles['36']:{
            'frame_start'  : [36],
            'num_frames'   : [181-36],
            'step'         : 300
                        },
        blendfiles['37'] :{
            'frame_start'  : [36],
            'num_frames'   : [260-36],
            'step'         : 300
                        },
        blendfiles['38'] :{
            'frame_start'  : [36],
            'num_frames'   : [213-36],
            'step'         : 300
                        },
        blendfiles['39'] :{
            'frame_start'  : [36],
            'num_frames'   : [253-36],
            'step'         : 300
                        },
        blendfiles['40']:{
            'frame_start'  : [36],
            'num_frames'   : [305-36],
            'step'         : 300
                        },
        blendfiles['41'] :{
            'frame_start'  : [36],
            'num_frames'   : [244-36],
            'step'         : 300
                        },
        blendfiles['42'] :{
            'frame_start'  : [36],
            'num_frames'   : [195-36],
            'step'         : 300
                        },
        blendfiles['43'] :{
            'frame_start'  : [82],
            'num_frames'   : [269-82],
            'step'         : 300
                        },
        blendfiles['44']:{
            'frame_start'  : [36],
            'num_frames'   : [202-36],
            'step'         : 300
                        },
        blendfiles['45'] :{
            'frame_start'  : [36],
            'num_frames'   : [278-36],
            'step'         : 300
                        },
        blendfiles['46'] :{
            'frame_start'  : [36],
            'num_frames'   : [202-36],
            'step'         : 300
                        },
            blendfiles['47'] :{
            'frame_start'  : [36],
            'num_frames'   : [215-36],
            'step'         : 300
                        },
        blendfiles['48']:{
            'frame_start'  : [36],
            'num_frames'   : [210-36],
            'step'         : 300
                        },
        blendfiles['49'] :{
            'frame_start'  : [36],
            'num_frames'   : [237-36],
            'step'         : 300
                        },
                    }
    
    mesh_order={
           blendfiles['0']: ['master_chef_can'],
           blendfiles['1']: ['master_chef_can'],
           blendfiles['2']: ['master_chef_can'],
           blendfiles['3']: ['cracker_box'],
           blendfiles['4']: ['cracker_box'],
           blendfiles['5']: ['sugar_box'],
           blendfiles['6']: ['sugar_box'],
           blendfiles['7']: ['sugar_box'],
           blendfiles['8']: ['tomato_soup_can'],
           blendfiles['9']: ['tomato_soup_can'],
           blendfiles['10']: ['tomato_soup_can'],
           blendfiles['11']: ['mustard_bottle'],
           blendfiles['12']: ['mustard_bottle'],
           blendfiles['13']: ['tuna_fish_can'],
           blendfiles['14']: ['tuna_fish_can'],
           blendfiles['15']: ['tuna_fish_can'],
           blendfiles['16']: ['pudding_box'],
           blendfiles['17']: ['pudding_box'],
           blendfiles['18']: ['pudding_box'],
           blendfiles['19']: ['gelatin_box'],
           blendfiles['20']: ['gelatin_box'],
           blendfiles['21']: ['potted_meat_can'],
           blendfiles['22']: ['potted_meat_can'],
           blendfiles['23']: ['banana'],
           blendfiles['24']: ['banana'],
           blendfiles['25']: ['pitcher_base'],
           blendfiles['26']: ['pitcher_base'],
           blendfiles['27']: ['pitcher_base'],
           blendfiles['28']: ['bleach_cleanser'],
           blendfiles['29']: ['bleach_cleanser'],
           blendfiles['30']: ['bowl'],
           blendfiles['31']: ['bowl'],
           blendfiles['32']: ['bowl'],
           blendfiles['33']: ['mug'],
           blendfiles['34']: ['mug'],
           blendfiles['35']: ['power_drill'],
           blendfiles['36']: ['power_drill'],
           blendfiles['37']: ['wood_block'],
           blendfiles['38']: ['wood_block'],
           blendfiles['39']: ['wood_block'],
           blendfiles['40']: ['scissors'],
           blendfiles['41']: ['scissors'],
           blendfiles['42']: ['large_marker'],
           blendfiles['43']: ['large_marker'],
           blendfiles['44']: ['extra_large_clamp'],
           blendfiles['45']: ['extra_large_clamp'],
           blendfiles['46']: ['extra_large_clamp'],
           blendfiles['47']: ['foam_brick'],
           blendfiles['48']: ['foam_brick'],
           blendfiles['49']: ['foam_brick'],
                }
    
    def __init__(self):
        self._chosen_blendfile = '0'
        self.update_related_variables()

    def setup_blenderproc_configuration(self):
        import logging
        
        import blenderproc as bproc

        bproc.init()


        if turn_on_coco_bop_annotations is True:
            # bproc.renderer.enable_distance_output(activate_antialiasing=True)
            bproc.renderer.enable_depth_output(activate_antialiasing=False, convert_to_distance=False)

    @property
    def chosen_blendfile(self):
        return self._chosen_blendfile
    
    @chosen_blendfile.setter
    def chosen_blendfile(self, value):
        self._chosen_blendfile = value
        self.update_related_variables()

    def update_related_variables(self):
        self.blendfilename = self.blendfiles[self._chosen_blendfile]
        self.frame_start = self.frame_settings[self.blendfilename]['frame_start']
        self.num_frames = self.frame_settings[self.blendfilename]['num_frames']
        self.step = self.frame_settings[self.blendfilename]['step']
        self.mesh_export_order = self.mesh_order[self.blendfilename]

config_instance = BlenderConfig()
