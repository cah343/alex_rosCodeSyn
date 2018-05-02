#!/usr/bin/env python

import yaml
import rospy
from geometry_msgs.msg import Twist
from math import radians
import os
#Function created a transform to convert the x and z velocities of a robot to another
scale = 1

#TO DO:
#Make scaling function

def get_yamls(robot1,robot2):
    #robot1 is the original robot
    #robot2 is the replacement robot1

    #get lin x and ang z limits for robot1 from yaml file
    with open("rosCodeSyn/config_files/yaml/" + robot1 + ".yaml", 'r') as stream:
        try:
            rob1_yaml = yaml.load(stream)
            #print(nao_yaml["linear"]["y"])
        except yaml.YAMLError as exc:
            print(exc)

    x_upper_rob1 = rob1_yaml["linear"]["x"]["upper"]
    x_lower_rob1 = rob1_yaml["linear"]["x"]["lower"]
    z_upper_rob1 = rob1_yaml["angular"]["z"]["upper"]
    z_lower_rob1 = rob1_yaml["angular"]["z"]["lower"]

    #get lin x and ang z limits for robot2 from yaml file
    with open("rosCodeSyn/config_files/yaml/"+ robot2 + ".yaml", 'r') as stream2:
        try:
            rob2_yaml = yaml.load(stream2)
            #print(jackal_yaml)
        except yaml.YAMLError as exc:
            print(exc)

    x_upper_rob2 = rob2_yaml["linear"]["x"]["upper"]
    x_lower_rob2 = rob2_yaml["linear"]["x"]["lower"]
    z_upper_rob2 = rob2_yaml["angular"]["z"]["upper"]
    z_lower_rob2 = rob2_yaml["angular"]["z"]["lower"]

    print(x_upper_rob1)
    print(x_upper_rob2)

def get_yaml(robot):
    #robot1 is the original robot
    #robot2 is the replacement robot1

    path_to_config_folder = os.path.dirname(os.path.abspath(__file__)) +'/rosCodeSyn/config_files/yaml/'
    #get lin x and ang z limits for robot1 from yaml file

    with open(path_to_config_folder + robot + ".yaml", 'r') as stream:
        try:
            rob_yaml = yaml.load(stream)
            #print(nao_yaml["linear"]["y"])
        except yaml.YAMLError as exc:
            print(exc)


    return rob_yaml


class rob_callback_class:

    def __init__(self, robot1, robot2, rob1_vel_topic):
        # initiliaze
        rospy.init_node('transform_rob2', anonymous=False)

        self.rob2_vel_pub = rospy.Publisher('/turtle2/cmd_vel', Twist, queue_size =10)
        rospy.Subscriber(rob1_vel_topic, Twist, self.rob_callback)

        rob1_yaml = get_yaml(robot1)
        rob2_yaml = get_yaml(robot2)

        self.x_upper_rob1 = rob1_yaml["linear"]["x"]["upper"]
        self.x_lower_rob1 = rob1_yaml["linear"]["x"]["lower"]
        self.z_upper_rob1 = rob1_yaml["angular"]["z"]["upper"]
        self.z_lower_rob1 = rob1_yaml["angular"]["z"]["lower"]

        self.x_upper_rob2 = rob2_yaml["linear"]["x"]["upper"]
        self.x_lower_rob2 = rob2_yaml["linear"]["x"]["lower"]
        self.z_upper_rob2 = rob2_yaml["angular"]["z"]["upper"]
        self.z_lower_rob2 = rob2_yaml["angular"]["z"]["lower"]

    def scaler(self):

        #scale = self.xvel_r1
        return scale

    def rob_callback(self,data):

        cmd_vel_rob2 = Twist()

        xvel_r1 = data.linear.x
        zvel_r1 = data.angular.z

        if xvel_r1 == 0:
            cmd_vel_rob2.linear.x = 0

        elif xvel_r1 > 0:
            scale_x = (xvel_r1)/(self.x_upper_rob1)
            cmd_vel_rob2.linear.x = scale_x*(self.x_upper_rob2)
        else:
            scale_x = (xvel_r1)/(self.x_lower_rob1)
            cmd_vel_rob2.linear.x = scale_x*self.x_lower_rob2



        if zvel_r1 == 0:
            cmd_vel_rob2.angular.z = 0

        elif zvel_r1 > 0:
            scale_z = (zvel_r1)/(self.z_upper_rob1)
            cmd_vel_rob2.angular.z = scale_z*(self.z_upper_rob2)

        else:
            scale_z = (zvel_r1)/(self.z_lower_rob1)
            cmd_vel_rob2.angular.z = scale_z*self.z_lower_rob2


        print(cmd_vel_rob2)

        self.rob2_vel_pub.publish(cmd_vel_rob2)


def main(robot1, robot2, rob1_vel_topic):



    rob1_callback = rob_callback_class(robot1, robot2, rob1_vel_topic)
    rospy.spin()


    #transform velocity message to map to limits of robot 2

    #publish velocity message for robot 2


    #ISSUE#
    #Scaling - jackal max = 2, nao max = 8. Jackal much much faster than nao. how to account?

if __name__ == "__main__":

    main("nao", "jackal", '/turtle1/cmd_vel')
