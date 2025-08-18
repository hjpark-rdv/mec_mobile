import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # ====== 패키지 경로 설정 ======
    pkg_mec_mobile_description = FindPackageShare('mec_mobile_description')
    pkg_mec_mobile_bringup = FindPackageShare('mec_mobile_bringup')

    # ====== 인자 (Arguments) ======
    default_model_path = PathJoinSubstitution([
        pkg_mec_mobile_description, 'urdf', 'robots', 'robot_3d_gz.urdf.xacro'
    ])
    default_controller_yaml_path = PathJoinSubstitution([
        pkg_mec_mobile_bringup, 'config', 'mecanum_controllers.yaml'
    ])

    model_arg = DeclareLaunchArgument('model', default_value=default_model_path)
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='true')
    gui_arg = DeclareLaunchArgument('gui', default_value='true')
    entity_arg = DeclareLaunchArgument('entity', default_value='mec_mobile')
    controller_yaml_arg = DeclareLaunchArgument(
        'controller_yaml_path', default_value=default_controller_yaml_path
    )

    # ====== Gazebo Sim 실행 ======
    # ✅ 수정: Gazebo에 불필요한 '--ros-args'를 전달하지 않음
    gz_sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
            ])
        ]),
        launch_arguments={'gz_args': '-r -v 4'}.items() # Gazebo 자체 옵션만 전달
    )

    # ====== Robot Description 생성 ======
    # ✅ 수정: URDF를 생성할 때 xacro에 컨트롤러 YAML 경로를 인자로 전달
    robot_description_content = ParameterValue(
        Command([
            'xacro ',
            LaunchConfiguration('model'),
            ' controller_yaml_path:=',
            LaunchConfiguration('controller_yaml_path')
        ]),
        value_type=str
    )

    # ====== Robot State Publisher 실행 ======
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_content,
                     'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    # ====== Gazebo에 로봇 스폰 ======
    spawn_entity_node = Node(
        package='ros_gz_sim',
        executable='create',
        name='gz_create',
        arguments=['-name', LaunchConfiguration('entity'),
                   '-topic', 'robot_description',
                   '-allow_renaming', 'true',
                   '-z', '0.05'],
        output='screen'
    )

    # ====== 컨트롤러 Spawner 실행 ======
    spawner_jsb = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen'
    )
    spawner_mecanum = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['mecanum_drive_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    # ====== LaunchDescription 반환 ======
    return LaunchDescription([
        model_arg,
        use_sim_time_arg,
        gui_arg,
        entity_arg,
        controller_yaml_arg,
        gz_sim_launch,
        robot_state_publisher_node,
        TimerAction(period=5.0, actions=[spawn_entity_node]),
        TimerAction(period=8.0, actions=[spawner_jsb]),
        TimerAction(period=9.0, actions=[spawner_mecanum]),
    ])