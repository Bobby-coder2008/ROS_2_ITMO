from launch import LaunchDescription
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_share = FindPackageShare('my_best_model')
    xacro_file = PathJoinSubstitution([
        package_share, 'urdf', 'robot_model.xacro'
    ])
    rviz_file = PathJoinSubstitution([
        package_share, 'rviz', 'robot.rviz'
    ])

    robot_description = Command([
        FindExecutable(name='xacro'), ' ', xacro_file
    ])

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            output='screen'
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_file],
            output='screen'
        )
    ])
