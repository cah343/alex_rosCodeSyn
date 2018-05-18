# alex_rosCodeSyn
Spring 2018 Project - ASL Cornell 
By: Alex Hirst 

**Purpose:** 

This package is designed to quickly remap a velocity publisher in order to transform its velocity messages to conform with specific limitations of a secondary robot.

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

In order to run your with your own script and robots: 

1. Install alex_rossyn_final.py (https://github.com/cah343/alex_rosCodeSyn)
2. Make sure all YAML files, control script, and alex_rossyn are in the same folder.
3. Start roscore
4. Change parameters in alex_rossyn_final.py to suit the original script, original robot name, and new robot name (Assumes YAML files are named [robot name].yaml and that they follow a format similar to the ones found in project repo)
5. Execute the program with $ rosrun [your package] alex_rossyn_final.py
6. The script should have generated a new script called:                 [original script name]_temp.py and executed said script. Alex_rossyn should be publishing a scaled message to the substitute robot via the original publisher topic. 


For More Information and Background on this package, see Final Report Link!

**Final Report Link:**

https://docs.google.com/document/d/13xJ8IvRljIN_3t05jniFGl2sjzz9OLfMx4ncn8qTnbw/edit?usp=sharinghttps://docs.google.com/document/d/13xJ8IvRljIN_3t05jniFGl2sjzz9OLfMx4ncn8qTnbw/edit?usp=sharing
