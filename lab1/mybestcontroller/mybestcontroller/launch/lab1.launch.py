om launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    isu_id = '502436'

    ns1 = 'ns1_' + isu_id
    ns2 = 'ns2_' + isu_id

    return LaunchDescription([

        Node(
            package='turtlesim',
            executable='turtlesim_node',
            namespace=ns1,
            name='turtlesim',
            output='screen'
        ),

        Node(
            package='mybestcontroller',
            executable='lab1_controller',
            namespace=ns1,
            name='controller',
            output='screen'
        ),

        Node(
            package='turtlesim',
            executable='turtlesim_node',
            namespace=ns2,
            name='turtlesim',
            output='screen'
        ),

        Node(
            package='mybestcontroller',
            executable='lab1_controller',
            namespace=ns2,
            name='controller',
            output='screen'
        )

    ])
