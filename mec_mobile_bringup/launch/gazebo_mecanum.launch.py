from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # ★ 기본 모델 경로: 사용자 환경(/home/hjpark/farm_ws/…)에 맞춰 둠
    default_model = '/home/hjpark/farm_ws/src/mec_mobile/mec_mobile_description/urdf/robots/robot_3d.urdf.xacro'

    model_arg = DeclareLaunchArgument(
        name='model',
        default_value=default_model,
        description='Path to URDF/Xacro file'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock'
    )

    # Gazebo (Classic) 실행
    gazebo_pkg = FindPackageShare('gazebo_ros')
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [PathJoinSubstitution([gazebo_pkg, 'launch', 'gazebo.launch.py'])]
        )
    )

    # xacro → robot_description (문자열로 고정해 YAML 파싱 오류 방지)
    robot_description_content = ParameterValue(
        Command(['xacro',' ', LaunchConfiguration('model')]),
        value_type=str
    )

    # (선택) TF 제공
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }],
        output='both'
    )

    # Gazebo에 로봇 스폰 (robot_description 토픽 사용)
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'mec_mobile'],
        output='screen'
    )

    # 컨트롤러 설정 파일
    controller_yaml = PathJoinSubstitution([
        FindPackageShare('mec_mobile_bringup'),
        'config',
        'mecanum_controllers.yaml'
    ])

    # 컨트롤러 스포너: JointStateBroadcaster → MecanumDriveController 순서로
    spawner_jsb = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager', '/controller_manager',
            '--param-file', controller_yaml
        ],
        output='screen'
    )

    spawner_mecanum = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'mecanum_drive_controller',
            '--controller-manager', '/controller_manager',
            '--param-file', controller_yaml
        ],
        output='screen'
    )

    # JSB가 올라간 뒤 메카넘 컨트롤러를 시작하도록 순서 보장
    chain_spawners = RegisterEventHandler(
        OnProcessExit(
            target_action=spawner_jsb,
            on_exit=[spawner_mecanum]
        )
    )

    return LaunchDescription([
        model_arg,
        use_sim_time_arg,
        gazebo_launch,
        robot_state_publisher,
        spawn_entity,
        spawner_jsb,
        chain_spawners,
    ])
