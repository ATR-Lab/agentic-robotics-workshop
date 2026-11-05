"""Wall-clock command watchdog between controller and simulator base bridge."""
import time
import rclpy
from rclpy.node import Node
from rclpy.clock import Clock, ClockType
from geometry_msgs.msg import TwistStamped

class Guard(Node):
    def __init__(self):
        super().__init__('command_guard')
        self.last=None; self.message=None
        self.pub=self.create_publisher(TwistStamped,'/base_cmd_vel',10)
        self.create_subscription(TwistStamped,'/cmd_vel',self.receive,10)
        self.create_timer(.05,self.tick,clock=Clock(clock_type=ClockType.STEADY_TIME))
    def receive(self,msg): self.last=time.monotonic(); self.message=msg
    def tick(self):
        msg=self.message if self.last is not None and time.monotonic()-self.last<.3 else TwistStamped()
        msg.header.stamp=self.get_clock().now().to_msg()
        self.pub.publish(msg)

def main():
    rclpy.init(); node=Guard()
    try: rclpy.spin(node)
    finally: node.destroy_node(); rclpy.shutdown()
