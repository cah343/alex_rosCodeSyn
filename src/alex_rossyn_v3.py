#!/usr/bin/env python

import yaml
import rospy
from geometry_msgs.msg import Twist
from math import radians
import os
import re
import matplotlib.pyplot as plt
import pandas as pd
import sys
import getpass
from shutil import copy2


#Function created a transform to convert the x and z velocities of a robot to another
scale = 1


# your codebase dir from param_config.py
#import param_config
#ROS_CODEBASES_DIR = param_config.ROS_CODEBASES_DIR

re_subscriber = re.compile(r'rospy\.Subscriber\([\'|\"](?P<topic>[\w_/]+)[\'|\"]\s?\,\s?(?P<msgType>[\w_.]+)')  # a pattern for subscriber
re_publisher = re.compile(r'rospy\.Publisher\([\'|\"](?P<topic>[\w_/]+)[\'|\"]\s?\,\s?(?P<msgType>[\w_.]+)')  # a pattern for publisher
re_act_client = re.compile(r'actionlib\.SimpleActionClient\([\'|\"](?P<action_topic>[\w_/]+)[\'|\"]\s?\,\s?(?P<msgType>[\w_.]+)')

def rewrite_and_return_vel_msg_pub_topic(file_name, re_compile_obj):
    """
    Replace old publishing topic name with new name. Returns old topic name for usage
        in new publisher
    new_topic_name: new topic name for original publisher
    file_path: path to python files (not recursive)
    re_compile_obj: list of re compile object to search for
    """

    line_to_append, line_to_check = "",""

    with open(os.path.dirname(os.path.abspath(__file__)) + "/" + file_name, "r") as fp, open("temp_" + file_name, "w+") as tempfp:

        copy2(file_name, "temp_"+file_name)

        for line in tempfp:

            # ignore comments
            if line.strip().startswith('#'):
                continue

            # concatenate line when necessary
            if line.strip().endswith('\\'):
                line_to_append += line.strip()[:-len('\\')]
            else:
                line_to_check = line_to_append+line.strip()
                line_to_append = ""

            if line_to_check:
                #print line_to_check
                #replace old publisher topic with new
                #TODO: match the topic group, return old topic, replace with new topic


                group_name_msg = re.search(re_compile_obj, line_to_check) #search for publisher

                if group_name_msg:

                    old_topic_name = group_name_msg.group('topic') #remember old publisher topic
                    print group_name_msg.group('topic')
                    line_to_check = re.sub(old_topic_name,'/new_topic',line_to_check)


                    print line_to_check
                    print line
                    print "publisher!"

                    #HELP HERE!!!!
                    # Write function do not overwrite current line, in fact they don't do anything

                    #tempfp.write(line_to_check)
                    tempfp.write(line_to_check.replace(old_topic_name, '/new_topic'))

                    
                    print line


                else:
                    #tempfp.write(line_to_check + '\n')
                    #print "No publisher"
                    print line_to_check


    tempfp.close()
    fp.close()
    return old_topic_name


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

    def scaler(self, xvel_data, zvel_data, twist_message):

        #input own scaling function here
        xlimU1 = self.x_upper_rob1
        xlimL1 = self.x_lower_rob1
        xlimU2 = self.x_upper_rob2
        xlimL2 = self.x_lower_rob2

        zlimU1 = self.z_upper_rob1
        zlimL1 = self.z_lower_rob1
        zlimU2 = self.z_upper_rob2
        zlimL2 = self.z_lower_rob2

        if xvel_data == 0:
            twist_message.linear.x = 0

        elif xvel_data > 0:
            scale_x = (xvel_data)/(xlimU1)
            twist_message.linear.x = scale_x*(xlimU2)
        else:
            scale_x = (xvel_r1)/(xlimL1)
            twist_message.linear.x = scale_x*xlimL2


        if zvel_data == 0:
            twist_message.angular.z = 0

        elif zvel_data > 0:
            scale_z = (zvel_data)/(zlimU1)
            twist_message.angular.z = scale_z*(zlimU2)
        else:
            scale_z = (zvel_r1)/(zlimL1)
            twist_message.angular.z = scale_z*zlimL2

        return twist_message

    def rob_callback(self,data):

        twist = Twist()

        xvel_r1 = data.linear.x
        zvel_r1 = data.angular.z

        cmd_vel_rob2 = self.scaler(xvel_r1, zvel_r1, twist)

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




    #Test the read function here(no replacement):
    old_topic = rewrite_and_return_vel_msg_pub_topic("drawsquare_tester.py", re_publisher)

    print old_topic

    #main("nao", "jackal", old_topic)


    #run file:
    #execfile("temp_drawsquare_tester.py")
