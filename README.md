# Adaptive AMCL for Long Corridor Navigation (ROS 2)

An experimental ROS 2 Humble project exploring an **adaptive localization strategy** 
for Autonomous Mobile Robots (AMRs) operating in long symmetric corridor environments.

The project investigates one of the common limitations of Adaptive Monte Carlo Localization (AMCL): 
localization uncertainty in environments where laser observations become highly repetitive. 
Instead of using fixed localization parameters, this work dynamically updates selected AMCL parameters at runtime
based on the detected environment.

> **Note**
>
> This project presents an adaptive strategy that I explored in simulation. It is intended as an engineering
>  investigation and has not been formally validated using quantitative localization metrics.

---

# Motivation

AMCL performs well in environments with distinctive geometric features.

However, localization becomes more challenging inside long corridors because laser scans collected at different 
positions often appear very similar.

```
+--------------------------------------------------------------+
|                                                              |
|                                                              |
|                                                              |
|                                                              |
+--------------------------------------------------------------+
```

In these environments, particle filters may experience:

- Increased localization uncertainty
- Slow convergence
- Particle spread
- Recovery behavior triggering more frequently

This project explores whether adapting AMCL parameters according to the surrounding environment can improve 
localization behavior.

---

# Proposed Approach

Instead of keeping AMCL parameters fixed throughout navigation, this project dynamically changes selected parameters 
based on the detected environment.

Pipeline

```
LiDAR Scan
      │
      ▼
Variance-Based Environment Analysis
      │
      ▼
Environment Classification
      │
 ┌───────────────┬────────────────┐
 │               │
 ▼               ▼
Symmetric     Non-Symmetric
(Corridor)    (Corners/Junctions)
 │               │
 └───────┬───────┘
         ▼
Update AMCL Parameters
         ▼
Continue Navigation
```

The parameter update is performed online using the ROS 2 Parameter Service without restarting AMCL.

---

# Features

- ROS 2 Humble
- Gazebo Sim
- Navigation2
- Adaptive Monte Carlo Localization (AMCL)
- Runtime Parameter Updates
- Three-Wheel Differential Drive Robot
- Long Corridor Environment
- LiDAR
- IMU
- Camera
- RViz2 Visualization
- Waypoint Patrol

---

# Repository Structure

```
adaptive-amcl-corridor-navigation/

├── robot_description
│
├── config
│
├── launch
│   ├── display.launch.py
│   └── navigation.launch.py
│
├── maps
│
├── rviz
│
├── scripts
│   ├── adaptive_amcl.py
│   └── corridor_patrol.py
│
├── urdf
│
├── worlds
│
├── package.xml
└── CMakeLists.txt
```

---

# Robot Configuration

Mobile Base

- Three-Wheel Differential Drive Robot

Sensors

- 2D LiDAR
- RGB Camera
- IMU

Navigation

- Navigation2
- AMCL
- Costmaps
- Planner Server
- Controller Server
- Behavior Tree Navigator

---

# Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Sim (Fortress)
- Navigation2
- ros_gz_sim
- ros_gz_bridge
- robot_state_publisher
- xacro

---

# Installation

Clone the repository inside your ROS 2 workspace.

```bash
cd ~/corridor_navigation_ws/src

git clone https://github.com/pawanshinde7218/adaptive-amcl-corridor-navigation.git
```

Build the workspace.

```bash
cd ~/corridor_navigation_ws

colcon build --symlink-install
```

Source the workspace.

```bash
source install/setup.bash
```

---

# How to Run the Project

The project consists of two launch files.

---

## Step 1 — Launch Simulation

This launch file starts

- Gazebo
- Robot Spawn
- Robot State Publisher
- Gazebo-ROS Bridge
- RViz

Run

```bash
ros2 launch robot_description display.launch.py
```

After launching, you should see

- Gazebo World
- Three-Wheel Robot
- RViz
- LiDAR Data
- Camera
- IMU
- TF Frames

---

## Step 2 — Launch Navigation2

Open a **new terminal**

```bash
source ~/corridor_navigation_ws/install/setup.bash
```

Launch Navigation2

```bash
ros2 launch robot_description nav.launch.py
```

This starts

- Map Server
- AMCL
- Planner Server
- Controller Server
- BT Navigator
- Recoveries
- Lifecycle Manager

---

# Adaptive AMCL

Run the adaptive localization node.

```bash
ros2 run robot_description env_classifier.py
```

This node

- Monitors incoming LiDAR scans
- Computes scan variance
- Classifies the environment
- Updates selected AMCL parameters dynamically through the ROS 2 Parameter Service

---

# Corridor Patrol

Run

```bash
ros2 run robot_description corridor_patrol.py
```

This node enables autonomous waypoint patrol.

Workflow

1. Click points in RViz using **Publish Point**
2. Each clicked point is stored in a list
3. The node sequentially sends navigation goals
4. Navigation goals are executed using the Nav2 NavigateToPose Action Server
5. After reaching the final waypoint, the patrol repeats

---

# Topics

| Topic | Description |
|---------|-------------|
| `/scan` | LiDAR Scan |
| `/odom` | Robot Odometry |
| `/cmd_vel` | Velocity Commands |
| `/map` | Occupancy Grid |
| `/tf` | TF Frames |
| `/clicked_point` | Patrol Waypoints |

---

# Current Assumptions

The current implementation assumes

- Wheel odometry provides a reasonable short-term estimate
- Corridor symmetry contributes to localization ambiguity
- Laser scan variance can be used as an indicator of environmental uniqueness

These assumptions are used only to investigate adaptive parameter tuning.

---

# Limitations

Current implementation

- Simulation only
- Variance-based environment classification
- Manually selected AMCL parameters
- No quantitative evaluation yet

---

# Future Work

- Adaptive Particle Count
- Particle Filter Entropy Analysis
- Automatic Confidence Estimation
- Learning-Based Environment Classification
- Dynamic Obstacles
- Real Robot Validation

---

# Technologies Used

- ROS 2 Humble
- Navigation2
- Gazebo Sim
- RViz2
- AMCL
- Python
- C++
- TF2
- ros_gz_bridge

---

# Screenshots

### Gazebo Simulation

<img width="1366" height="768" alt="Screenshot from 2026-07-14 10-39-00" src="https://github.com/user-attachments/assets/3eeb01b2-3fa9-4f8f-b857-6938374cf6b3" />


---

### RViz Navigation

<img width="1366" height="768" alt="Screenshot from 2026-07-14 10-38-40" src="https://github.com/user-attachments/assets/ddeea18a-9076-4530-be6e-b7558c88e69a" />


---

### Adaptive Parameter Update & Waypoint Patrol

<img width="1366" height="768" alt="Screenshot from 2026-07-14 10-37-33" src="https://github.com/user-attachments/assets/fa5b3fcd-7965-4cfb-9df6-4c05d2b6f651" />


---

# Author

**Pawan Shinde**

Automation & Robotics Engineer

Interested in

- Autonomous Mobile Robots
- Localization
- Navigation
- Robot Software Engineering
- ROS 2

GitHub

https://github.com/pawanshinde7218

LinkedIn

https://linkedin.com/in/pawan-shinde-ps12
