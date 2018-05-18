# alex_rosCodeSyn
Spring 2018 Project - ASL Cornell 
By: Alex Hirst 

**Purpose:** 

This package is designed to quickly remap a velocity publisher in order to transform its velocity messages to conform with specific limitations of a secondary...
robot.

**Software Requirements:** 

- ROS Kinetic

**Demo Instructions:** 

In order to run turtlesim demo:

1. Start roscore
2. $ roslaunch alex_rossyn multi_turtlesim.launch
3. Navigate new terminal to ~/alex_rossyn/src
4. $ rosrun alex_rossyn alex_rossyn_v4.py

In order to run gazebo demo:

1. Start roscore 
2. $ roslaunch turtlebot_gazebo turtlebot_world.launch
3. Navigate new terminal to ~/alex_rossyn/src
4. $ rosrun alex_rossyn alex_rossyn_v5.py
