import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
 
def generate_launch_description():
    my_pkg_dir = get_package_share_directory('robot_description')
    nav2_params_path = os.path.join(my_pkg_dir, 'config', 'nav_param.yaml')
    map_path = os.path.join(my_pkg_dir, 'map', 'new_map.yaml')
    
    nav2_launch_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav2_launch_dir, 'bringup_launch.py')),
            launch_arguments={
                'map': map_path,
                'params_file': nav2_params_path,
                'use_sim_time': 'true',  
            }.items()
        ),
    ])
 
 