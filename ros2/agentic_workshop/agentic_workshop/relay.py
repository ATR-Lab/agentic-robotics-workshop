"""Explicit simulator fault-injection relay; never used with physical hardware."""
import copy
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

class Relay(Node):
    def __init__(self):
        super().__init__('scan_relay'); self.declare_parameter('mode','pass')
        self.pub=self.create_publisher(LaserScan,'/workshop/scan',qos_profile_sensor_data)
        self.create_subscription(LaserScan,'/scan',self.receive,qos_profile_sensor_data)
    def receive(self,msg):
        mode=self.get_parameter('mode').value
        if mode=='drop': return
        msg=copy.deepcopy(msg)
        if mode=='invalid': msg.ranges=[float('nan')]*len(msg.ranges)
        if mode=='missing_tf': msg.header.frame_id='deliberately_missing_frame'
        self.pub.publish(msg)

def main():
    rclpy.init(); node=Relay()
    try: rclpy.spin(node)
    finally: node.destroy_node(); rclpy.shutdown()
