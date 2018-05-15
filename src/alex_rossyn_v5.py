#!/usr/bin/env python

"""
Code Written By: Alex Hirst (cah343)
ASL, Cornell University, Spring 2018
Takes in two robot YAML files, remaps original control script to publish to a
different topic, reads new topic, scales velocity message, and then republishes
the scaled velocity message to the old topic.
"""

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
import subprocess
import stat



#Scaling constant for velocity messages
scale = 1



#Define re objects to search for in old control script
re_subscriber = re.compile(r'rospy\.Subscriber\([\'|\"](?P<topic>[\w_/]+)[\'|\"]\s?\,\s?(?P<msgType>[\w_.]+)')  # a pattern for subscriber
re_publisher = re.compile(r'rospy\.Publisher\([\'|\"](?P<topic>[\w_/]+)[\'|\"]\s?\,\s?(?P<msgType>[\w_.]+)')  # a pattern for publisher
re_act_client = re.compile(r'actionlib\.SimpleActionClient\([\'|\"](?P<action_topic>[\w_/]+)[\'|\"]\s?\,\s?(?P<msgType>[\w_.]+)')


def number_of_spacesandtabs(line):

    #This function is unutilized in this project, but may be helpful for someone else

    print line
    #initialize
    #length_with_whitespace = 0
    #length_without_whitespace = 0

    #length_with_spaces = 0
    #length_without_spaces = 0
    #length_with_tabs = 0
    #length_without_tabs = 0

    #number_spaces = 0
    #number_tabs = 0
    #exp_line = line.expandtabs(4)

    #find number of spaces:
    #length_with_spaces = len(line)
    #length_without_spaces = len(line.lstrip('/s')) #strip spaces
    #number_spaces = length_with_spaces-length_without_spaces
    #print "space: " + str(number_spaces)

    #length_with_tabs = len(line)
    #length_without_tabs = len(line.lstrip('/t')) #strip tabs
    #number_tabs = length_with_tabs-length_without_tabs
    #print number_tabs

    # ignore comments
    #if line.strip().startswith('#'):
        #continue

    # concatenate line when necessary
    #if line.strip().endswith('\\'):
        #line_to_append += line.strip()[:-len('\\')]
    #else:
        #line_to_check = line_to_append+line.strip()
        #line_to_append = ""


def rewrite_and_return_vel_msg_pub_topic(file_name, re_compile_obj):
    """
    Replace old publishing topic name with new name. Returns old topic name for usage
        in new publisher
    new_topic_name: new topic name for original publisher
    file_path: path to python files (not recursive)
    re_compile_obj: list of re compile object to search for
    file created will have the name temp_[old_file_name].py
    """

    line_to_append, line_to_check = "",""

    #Open old control file (fp) and new file to write to (temp_fp)
    with open(os.path.dirname(os.path.abspath(__file__)) + "/" + file_name, "r") as fp, open("temp_" + file_name, "w+") as tempfp:


        for line in fp:
            line_to_check = line
            if line_to_check:

                group_name_msg = re.search(re_compile_obj, line_to_check) #search for publisher

                if group_name_msg:

                    old_topic_name = group_name_msg.group('topic') #remember old publisher topic
                    #print group_name_msg.group('topic')

                    #rename old publisher to old_topic_name+temp
                    line_to_check = re.sub(old_topic_name,old_topic_name+ "_temp",line_to_check)

                    print "publisher found!"
                    tempfp.write(line_to_check + '\n')


                else:
                    #tempfp.write('\t'*number_tabs + '\s'*number_spaces + line_to_check + '\n')
                    print "No publisher"
                    #print line_to_check
                    tempfp.write(line_to_check + '\n')

            else:
                #tempfp.write('\t'*number_tabs + '\s'*number_spaces + line + '\n')
                tempfp.write(line + '\n')

    #Close files
    tempfp.close()
    fp.close()

    #make file executable
    st = os.stat("temp_"+file_name)
    os.chmod("temp_" + file_name, st.st_mode | stat.S_IEXEC)

    #return old topic name for use in new publisher
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
    #get the yaml file for one robot

    path_to_config_folder = os.path.dirname(os.path.abspath(__file__)) +'/rosCodeSyn/config_files/yaml/'
    #get lin x and ang z limits for robot1 from yaml file

    with open(path_to_config_folder + robot + ".yaml", 'r') as stream:
        try:
            rob_yaml = yaml.load(stream)
            #print(nao_yaml["linear"]["y"])
        except yaml.YAMLError as exc:
            print(exc)

    #return yaml file
    return rob_yaml

class rob_callback_class:

    """
This class contains the new publisher and the scaling function in order to
scale and publish the transformed velocity command
    """

    #initialize object
    def __init__(self, robot1, robot2, rob1_vel_topic):
        print 'callback object initiliazed'
        print 'begin publishing'


        rospy.init_node('alex_rossyn', anonymous=False)

        self.rob2_vel_pub = rospy.Publisher(rob1_vel_topic, Twist, queue_size =10)
        rospy.Subscriber(rob1_vel_topic+"_temp", Twist, self.rob_callback)

        #get robot parameters from yaml files
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
            scale_x = (xvel_data)/(xlimL1)
            twist_message.linear.x = scale_x*xlimL2


        if zvel_data == 0:
            twist_message.angular.z = 0

        elif zvel_data > 0:
            scale_z = (zvel_data)/(zlimU1)
            twist_message.angular.z = scale_z*(zlimU2)
        else:
            scale_z = (zvel_data)/(zlimL1)
            twist_message.angular.z = scale_z*zlimL2

        #return scaled velocity message
        return twist_message

    def rob_callback(self,data):

        twist = Twist()

        #retrieve x and z velocities
        xvel_r1 = data.linear.x
        zvel_r1 = data.angular.z

        #scale velocity command
        cmd_vel_rob2 = self.scaler(xvel_r1, zvel_r1, twist)

        print(cmd_vel_rob2)

        #publish scaled velocity command
        self.rob2_vel_pub.publish(cmd_vel_rob2)


def main(robot1, robot2, rob1_vel_topic, old_script):


    print "started main function"

    #run temp script
    temp_script = "temp_" + old_script
    subprocess.Popen(["rosrun", "alex_rossyn", temp_script])
    print "temp script ran"

    #start callback
    rob1_callback = rob_callback_class(robot1, robot2, rob1_vel_topic)
    rospy.spin()


if __name__ == "__main__":

    old_robot_name = "nao"
    new_robot_name = "jackal"
    old_script = "turtlebot_auto_drive_tester.py"

    #Test the read function here(no replacement):
    old_topic = rewrite_and_return_vel_msg_pub_topic(old_script, re_publisher)
    print "Old Topic: " + old_topic

    #run file:
    main(old_robot_name, new_robot_name, old_topic, old_script)
