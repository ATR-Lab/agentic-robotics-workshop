import time
import math
import rclpy
from rclpy.node import Node
from rclpy.clock import Clock, ClockType
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import String
from tf2_ros import Buffer, TransformListener, TransformException
from .common import stamp_seconds, transform_point, publish_json, sector, decode_cloud

class CloudDiagnostic(Node):
    def __init__(self):
        super().__init__('cloud_diagnostic')
        for key,value in [('cloud_topic','/unilidar/cloud'),('target_frame','base_link'),
                          ('max_age',.25),('receive_timeout',.5),('threshold',.5),
                          ('half_angle',30.),('z_min',.05),('z_max',.5)]:
            self.declare_parameter(key,value)
        self.tf = Buffer(); self.listener = TransformListener(self.tf,self)
        self.pub = self.create_publisher(String,'/workshop/cloud_status',10)
        self.create_subscription(PointCloud2,self.p('cloud_topic'),self.receive,qos_profile_sensor_data)
        self.last = None; self.received = None; self.result = ('unknown',None,0)
        self.reason = 'no_data'
        self.create_timer(.1,self.tick,clock=Clock(clock_type=ClockType.STEADY_TIME))

    def p(self,key): return self.get_parameter(key).value

    def receive(self,msg):
        self.received = time.monotonic(); self.last = stamp_seconds(msg.header.stamp)
        try:
            points = decode_cloud(msg)
            if not msg.header.frame_id: raise ValueError('empty frame')
            if msg.header.frame_id != self.p('target_frame'):
                tf = self.tf.lookup_transform(self.p('target_frame'),msg.header.frame_id,
                                              Time.from_msg(msg.header.stamp)).transform
                points = [transform_point(p,tf) for p in points]
            self.result = sector(points,self.p('threshold'),self.p('half_angle'),self.p('z_min'),self.p('z_max'))
            self.reason = 'ok' if self.result[0]!='unknown' else 'no_valid_points'
        except (TransformException, ValueError, TypeError, AssertionError, KeyError) as exc:
            self.result = ('unknown',None,0); self.reason = 'decode_or_tf:'+type(exc).__name__

    def tick(self):
        age = None if self.last is None else self.get_clock().now().nanoseconds*1e-9-self.last
        state,distance,count = self.result
        reason = self.reason
        if age is None or not math.isfinite(age) or not 0 <= age <= self.p('max_age'):
            state,distance,count,reason = 'unknown',None,0,'timestamp_age'
        if self.received is None or time.monotonic()-self.received > self.p('receive_timeout'):
            state,distance,count,reason = 'unknown',None,0,'receive_timeout'
        publish_json(self.pub,state=state,distance=distance,count=count,age=age,reason=reason)

def main():
    rclpy.init(); node=CloudDiagnostic()
    try: rclpy.spin(node)
    finally: node.destroy_node(); rclpy.shutdown()
