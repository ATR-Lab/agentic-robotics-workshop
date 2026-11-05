import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory as share

def generate_launch_description():
    tb=share('turtlebot3_gazebo'); ours=share('agentic_workshop')
    gz=share('ros_gz_sim')
    return LaunchDescription([
        SetEnvironmentVariable('TURTLEBOT3_MODEL','burger'),
        SetEnvironmentVariable('GZ_IP','127.0.0.1'),
        SetEnvironmentVariable('GZ_PARTITION','agentic_workshop'),
        SetEnvironmentVariable('LIBGL_ALWAYS_SOFTWARE','1'),
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH',os.path.join(tb,'models')),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(gz,'launch','gz_sim.launch.py')),
            launch_arguments={'gz_args':'-r -s --headless-rendering '+os.path.join(ours,'worlds','corridor.sdf')}.items()),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(os.path.join(tb,'launch','robot_state_publisher.launch.py')),
            launch_arguments={'use_sim_time':'true'}.items()),
        Node(package='ros_gz_sim',executable='create',arguments=['-name','burger','-file',os.path.join(tb,'models','turtlebot3_burger','model.sdf'),'-z','.01']),
        Node(package='ros_gz_bridge',executable='parameter_bridge',arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model']),
        Node(package='ros_gz_bridge',executable='parameter_bridge',arguments=['/cmd_vel@geometry_msgs/msg/TwistStamped]gz.msgs.Twist'],remappings=[('/cmd_vel','/base_cmd_vel')]),
        Node(package='agentic_workshop',executable='scan_relay',parameters=[{'use_sim_time':True}]),
        Node(package='agentic_workshop',executable='command_guard',parameters=[{'use_sim_time':True}]),
        Node(package='agentic_workshop',executable='bounded_controller',parameters=[{'use_sim_time':True,'scan_topic':'/workshop/scan'}]),
    ])
