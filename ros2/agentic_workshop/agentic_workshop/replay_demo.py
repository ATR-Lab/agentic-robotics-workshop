"""Create a labeled synthetic bag, play it through ROS and assert diagnostic results."""
import argparse
import json
import os
import struct
import signal
import subprocess
import time
from pathlib import Path
import rclpy
import rosbag2_py
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.serialization import serialize_message
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import String
from rosgraph_msgs.msg import Clock
from geometry_msgs.msg import TransformStamped
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    args=parser.parse_args(); out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    bag=out/'synthetic_cloud_bag'
    if bag.exists(): raise SystemExit('Use a new output directory; existing bags are preserved')
    writer=rosbag2_py.SequentialWriter()
    writer.open(rosbag2_py.StorageOptions(uri=str(bag),storage_id='sqlite3'),rosbag2_py.ConverterOptions('',''))
    writer.create_topic(rosbag2_py.TopicMetadata(name='/unilidar/cloud',type='sensor_msgs/msg/PointCloud2',serialization_format='cdr',id=0))
    phases=[('clear',[(0,.2,.2),(1,0,.2)],'sensor'),
            ('blocked',[(.25,0,.2)],'sensor'),('unknown',[],'sensor'),
            ('unknown',[(1,0,.2)],'missing_frame'),
            ('clear',[(1,0,.2),(2,0,.2)],'sensor'),
            ('unknown',[(1,0,.2)],'sensor'),('unknown',[(1,0,.2)],'sensor')]
    for phase,(state,points,frame) in enumerate(phases):
        for index in range(20):
            timestamp=10+phase*2+index*.1
            msg=PointCloud2(); msg.header.frame_id=frame
            stamp=timestamp + (-1. if phase==5 else .5 if phase==6 else 0.)
            msg.header.stamp.sec=int(stamp); msg.header.stamp.nanosec=int(round((stamp-int(stamp))*1e9))
            msg.height=1; msg.width=len(points); msg.point_step=32; msg.row_step=32*len(points)
            msg.fields=[PointField(name=n,offset=o,datatype=PointField.FLOAT32,count=1) for n,o in [('x',0),('y',4),('z',8),('intensity',16)]]
            msg.data=b''.join(struct.pack('<fff4xf12x',*point,1.) for point in points)
            if phase==4:
                msg.is_bigendian=True; msg.width=1; msg.height=2; msg.row_step=40
                msg.data=b''.join(struct.pack('>fff4xf12x',*point,1.)+bytes(8) for point in points)
            writer.write('/unilidar/cloud',serialize_message(msg),int(timestamp*1e9))
    del writer
    rclpy.init(); node=Node('replay_verifier'); observed={i:[] for i in range(len(phases))}; current=[0.]
    node.create_subscription(Clock,'/clock',lambda m: current.__setitem__(0,m.clock.sec+m.clock.nanosec*1e-9),qos_profile_sensor_data)
    all_rows=[]
    def receive(msg):
        row=json.loads(msg.data); row['clock']=current[0]; all_rows.append(row)
        phase=int((current[0]-10)//2)
        if 0<=phase<len(phases) and current[0] >=10+phase*2+.4:
            observed[phase].append(row['state'])
    node.create_subscription(String,'/workshop/cloud_status',receive,10)
    broadcaster=StaticTransformBroadcaster(node)
    tf=TransformStamped(); tf.header.frame_id='base_link'; tf.child_frame_id='sensor'
    tf.transform.translation.x=.1; tf.transform.rotation.w=1.; broadcaster.sendTransform(tf)
    log=open(out/'diagnostic.log','w')
    env=dict(os.environ)
    process=subprocess.Popen(['ros2','run','agentic_workshop','cloud_diagnostic','--ros-args','-p','use_sim_time:=true'],stdout=log,stderr=log,env=env,start_new_session=True)
    player=None
    try:
        deadline=time.monotonic()+2
        while time.monotonic()<deadline: rclpy.spin_once(node,timeout_sec=.05)
        player=subprocess.Popen(['ros2','bag','play',str(bag),'--clock','100','--delay','2'],stdout=log,stderr=log,env=env,start_new_session=True)
        deadline=time.monotonic()+25
        while time.monotonic()<deadline and player.poll() is None: rclpy.spin_once(node,timeout_sec=.05)
        deadline=time.monotonic()+1
        while time.monotonic()<deadline: rclpy.spin_once(node,timeout_sec=.05)
        checks={str(i):{'expected':phase[0],'seen':sorted(set(observed[i])),
                       'pass':set(observed[i])=={phase[0]}} for i,phase in enumerate(phases)}
        checks['tf_translation']={'pass':any(r['state']=='clear' and r['distance'] is not None and abs(r['distance']-1.1)<.001 for r in all_rows)}
        checks['receive_timeout']={'pass':bool(all_rows) and all_rows[-1]['reason']=='receive_timeout'}
        report={'provenance':'authored synthetic PointCloud2; not Unitree hardware capture','checks':checks,'messages':len(all_rows)}
        (out/'replay-report.json').write_text(json.dumps(report,indent=2))
        (out/'replay-events.json').write_text(json.dumps(all_rows,indent=2))
        print(json.dumps(report,indent=2))
        if not all(c['pass'] for c in checks.values()): raise SystemExit(1)
    finally:
        for p in (player,process):
            if p is not None and p.poll() is None: os.killpg(p.pid,signal.SIGTERM); p.wait(timeout=10)
        log.close(); node.destroy_node(); rclpy.shutdown()
