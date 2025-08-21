# mec_mobile #

This repository is for creating a Mecanum Mobile Robot with URDF and Visualize it in RViz.

- Platform: ROS2 Jazzy + Gazebo Harmonic

[Here is the step by step tutrorial video on Youtube](https://youtu.be/ABLQZkkTKlI)

Use the main branch as the start package for Gazebo simulation

## Quick Start

* Create a ros workspace
    ```bash   
    mkdir -p ~/ros2_ws/src
    cd ~/ros2_ws/src
    ```
* Download the package
    ```bash    
    git clone -b main https://github.com/roboticslabs/mec_mobile.git
    ```
* Compile the package
    ```bash
    cd ~/ros2_ws
    sudo apt-get install ros-${ROS_DISTRO}-urdf-tutorial ros-humble-controller-manager
    colcon build
    ```
* Try it
    ```bash
    source ~/ros2_ws/install/setup.bash
    ros2 launch urdf_tutorial display.launch.py model:=/home/robotlabs/ros2_ws/src/mec_mobile/mec_mobile_description/urdf/robots/robot_3d.urdf.xacro
    ```
    Note: update the model's path according to your own setting.

## GAZEBO SIM 

* compile package
   ```bash
   rosdep install -i --from-path src --rosdistro humble
   ```

* gazebo sim, run
    ```bash
    ros2 launch mec_mobile_bringup gazebo_mecanum_gz.launch.py
    ```

* gazebo sim, simple test
    ```bash
    ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=True --remap cmd_vel:=/mecanum_drive_controller/reference
    ```

* (WSL with OGRE2 에러 날때)
    ```bash
    add-apt-repository ppa:kisak/turtle \
    && apt-get update \
    && apt-get upgrade -y 
    #mesa driver ver25로 업그레이드 이후 아래 export 수행
    export GALLIUM_DRIVER=d3d12
    export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA
    ```
