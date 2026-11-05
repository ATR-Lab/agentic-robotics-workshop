import os
import math
import time
import rclpy
from rclpy.node import Node
from rclpy.clock import Clock, ClockType
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from rcl_interfaces.msg import SetParametersResult
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist, TwistStamped
from std_msgs.msg import String
from std_srvs.srv import Trigger
from tf2_ros import Buffer, TransformListener, TransformException
from .common import stamp_seconds, transform_point, publish_json

class Controller(Node):
    def __init__(self):
        super().__init__('bounded_controller')
        for key,value in [('scan_topic','/scan'),('odom_topic','/odom'),('cmd_topic','/cmd_vel'),
                          ('stamped',True),('base_frame','base_footprint'),('speed',.1),
                          ('max_distance',.45),('max_duration',10.),('max_age',.5),
                          ('front_extent',.11),('half_width',.15),('stop_gap',.3)]:
            self.declare_parameter(key,value)
        self.add_on_set_parameters_callback(self.validate)
        checked=self.validate([self.get_parameter(k) for k in ('speed','max_distance','max_duration','max_age','front_extent','half_width','stop_gap')])
        if not checked.successful: raise ValueError(checked.reason)
        self.tf=Buffer(); self.listener=TransformListener(self.tf,self)
        self.cmd=self.create_publisher(TwistStamped if self.p('stamped') else Twist,self.p('cmd_topic'),10)
        self.status=self.create_publisher(String,'/workshop/controller_status',10)
        self.create_subscription(LaserScan,self.p('scan_topic'),self.scan,qos_profile_sensor_data)
        self.create_subscription(Odometry,self.p('odom_topic'),self.odom,qos_profile_sensor_data)
        self.state='idle'; self.reason='not_started'; self.gap=None
        self.scan_received=None; self.scan_stamp=None; self.odom_received=None; self.odom_stamp=None
        self.position=None; self.origin=None; self.started=None
        for name,method in [('start',self.start),('stop',self.stop),('reset',self.reset)]:
            self.create_service(Trigger,'/workshop/'+name,method)
        self.create_timer(.05,self.tick,clock=Clock(clock_type=ClockType.STEADY_TIME))

    def validate(self,parameters):
        limits={'speed':(.001,.2),'max_distance':(.01,5.),'max_duration':(.1,60.),'max_age':(.05,2.),'front_extent':(.01,.5),'half_width':(.05,.5),'stop_gap':(.05,2.)}
        for param in parameters:
            if param.name in limits:
                low,high=limits[param.name]
                if not isinstance(param.value,(int,float)) or not math.isfinite(param.value) or not low<=param.value<=high:
                    return SetParametersResult(successful=False,reason='value outside simulator exercise bounds')
        return SetParametersResult(successful=True)

    def p(self,k): return self.get_parameter(k).value
    def ros_now(self): return self.get_clock().now().nanoseconds*1e-9
    def fresh(self,received,stamp):
        return (received is not None and stamp is not None and
                time.monotonic()-received <= self.p('max_age') and
                0 <= self.ros_now()-stamp <= self.p('max_age'))
    def odom(self,msg):
        p=msg.pose.pose.position
        if all(math.isfinite(v) for v in (p.x,p.y)):
            self.position=(p.x,p.y); self.odom_received=time.monotonic()
            self.odom_stamp=stamp_seconds(msg.header.stamp)
    def scan(self,msg):
        self.scan_received=time.monotonic(); self.scan_stamp=stamp_seconds(msg.header.stamp)
        self.gap=None
        try:
            tf=None
            if msg.header.frame_id != self.p('base_frame'):
                tf=self.tf.lookup_transform(self.p('base_frame'),msg.header.frame_id,
                                            Time.from_msg(msg.header.stamp)).transform
            gaps=[]; coverage=0
            for i,r in enumerate(msg.ranges):
                a=msg.angle_min+i*msg.angle_increment
                if math.isnan(r) or r == -math.inf or r < msg.range_min: continue
                if r == math.inf: r=msg.range_max
                if not math.isfinite(r) or r > msg.range_max: continue
                point=(r*math.cos(a),r*math.sin(a),0.)
                x,y,z=transform_point(point,tf) if tf else point
                if abs(a) <= math.radians(30): coverage+=1
                if x >= 0 and abs(y)<=self.p('half_width'):
                    gaps.append(x-self.p('front_extent'))
            if coverage>=5: self.gap=min(gaps) if gaps else float(msg.range_max)-self.p('front_extent')
        except (TransformException,ValueError): pass
    def start(self,request,response):
        ok=(self.state=='idle' and self.gap is not None and self.gap>self.p('stop_gap')
            and self.fresh(self.scan_received,self.scan_stamp) and self.fresh(self.odom_received,self.odom_stamp))
        response.success=ok; response.message='started' if ok else 'reset and supply fresh clear sensing/odometry'
        if ok:
            self.state='advance'; self.origin=self.position; self.started=self.ros_now(); self.reason='running'
        return response
    def stop(self,request,response):
        self.state='stopped'; self.reason='operator_stop'; self.command(0.)
        response.success=True; return response
    def reset(self,request,response):
        self.state='idle'; self.reason='reset'; self.command(0.)
        response.success=True; return response
    def command(self,speed):
        msg=TwistStamped() if self.p('stamped') else Twist()
        twist=msg.twist if self.p('stamped') else msg
        twist.linear.x=float(speed)
        if self.p('stamped'): msg.header.stamp=self.get_clock().now().to_msg()
        self.cmd.publish(msg)
    def tick(self):
        distance=0. if self.origin is None or self.position is None else math.dist(self.origin,self.position)
        if self.state=='advance':
            if not (self.fresh(self.scan_received,self.scan_stamp) and self.fresh(self.odom_received,self.odom_stamp)) or self.gap is None:
                self.state='fault'; self.reason='sensing_or_tf'
            elif self.gap<=self.p('stop_gap'): self.state='stopped'; self.reason='obstacle'
            elif distance>=self.p('max_distance'): self.state='stopped'; self.reason='distance_bound'
            elif self.ros_now()-self.started>=self.p('max_duration'): self.state='stopped'; self.reason='time_bound'
        speed=self.p('speed') if self.state=='advance' else 0.
        self.command(speed)
        publish_json(self.status,pid=os.getpid(),state=self.state,reason=self.reason,command=speed,distance=distance,gap=self.gap)

def main():
    rclpy.init(); node=Controller()
    try: rclpy.spin(node)
    finally:
        node.command(0.); node.destroy_node(); rclpy.shutdown()
