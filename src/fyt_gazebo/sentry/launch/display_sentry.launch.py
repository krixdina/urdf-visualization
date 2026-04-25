from ament_index_python.packages import get_package_share_path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition,UnlessCondition
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    sentry_path = get_package_share_path('sentry')
    default_model_path = sentry_path/'urdf'/'sentry.urdf'
    default_rviz_config_path = sentry_path/'rviz'/'urdf.rviz'

    # 声明会影响到后续节点启动的几个参数
    gui_arg = DeclareLaunchArgument(name='gui', default_value='true', choices=['true' , 'false'],
                                    description='Flag to enable joint_state_publisher_gui')
    
    model_arg = DeclareLaunchArgument(name='model', default_value=str(default_model_path),
                                      description='Absolute path to robot urdf file')
    
    rviz_arg = DeclareLaunchArgument(name='rvizconfig' , default_value=str(default_rviz_config_path),
                                     description= 'Absolute path to rviz config file')
    
    # 可以动态的通过命令行切换模型
    # 进入urdf目录
    # ros2 launch urdf_tutorial display.launch.py model:=urdf/***.urdf

    # 需要在xacro后多输入一个空格，否则会找不到文件
    robot_description = ParameterValue(Command(['xacro ' , LaunchConfiguration('model')]),
                                       value_type=str)

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description' : robot_description}]
    )

    #此处两个节点的启动依赖于gui参数值
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        condition=UnlessCondition(LaunchConfiguration('gui'))
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        condition= IfCondition(LaunchConfiguration('gui'))
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        # 启动 rviz2 节点时，通过命令行传递 -d 选项，后面紧跟着配置文件的绝对路径
        arguments=['-d',LaunchConfiguration('rvizconfig')],
    )

    return LaunchDescription([
        gui_arg,
        model_arg,
        rviz_arg,
        joint_state_publisher_node,
        joint_state_publisher_gui_node,
        robot_state_publisher_node,
        rviz_node
    ])
