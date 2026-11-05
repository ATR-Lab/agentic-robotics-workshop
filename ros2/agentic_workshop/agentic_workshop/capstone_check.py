"""Observe Gazebo motion and inject explicit simulator-only failure scenarios."""
import argparse
import json
import math
import os
import signal
import time
from pathlib import Path
import rclpy
from rclpy.node import Node
from rcl_interfaces.srv import SetParameters
from rclpy.parameter import Parameter
from std_msgs.msg import String
from std_srvs.srv import Trigger
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TwistStamped

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--output',required=True)
    args=parser.parse_args(); out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    rclpy.init(); node=Node('capstone_verifier'); status=[{}]; position=[None]; base=[None]; rows=[]; results=[]
    def on_status(msg):
        row=json.loads(msg.data); row['wall_time']=time.time(); status[0]=row; rows.append(row)
    node.create_subscription(String,'/workshop/controller_status',on_status,10)
    node.create_subscription(Odometry,'/odom',lambda m: position.__setitem__(0,(m.pose.pose.position.x,m.pose.pose.position.y)),10)
    node.create_subscription(TwistStamped,'/base_cmd_vel',lambda m:base.__setitem__(0,m.twist.linear.x),10)
    def spin(seconds):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline: rclpy.spin_once(node,timeout_sec=.05)
    def until(predicate,timeout=30):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            rclpy.spin_once(node,timeout_sec=.05)
            if predicate(): return
        raise AssertionError('Timed out; latest status: '+str(status[0]))
    def call(path,service,request):
        client=node.create_client(service,path)
        if not client.wait_for_service(timeout_sec=15): raise AssertionError('Missing service '+path)
        future=client.call_async(request); until(future.done,15)
        result=future.result(); node.destroy_client(client); return result
    def trigger(name):
        result=call('/workshop/'+name,Trigger,Trigger.Request())
        assert result.success,(name,result.message)
        spin(.2)
    def param(target,name,value):
        request=SetParameters.Request(parameters=[Parameter(name,value=value).to_parameter_msg()])
        response=call('/'+target+'/set_parameters',SetParameters,request)
        assert all(r.successful for r in response.results)
        spin(.3)
    def record(name,**data):
        result={'scenario':name,'pass':True,'status':status[0],**data}; results.append(result); print(json.dumps(result),flush=True)
    stopped_pid=None
    try:
        until(lambda:position[0] is not None and status[0].get('gap') is not None,90)
        request=SetParameters.Request(parameters=[Parameter('speed',value=-1.).to_parameter_msg()])
        rejected=call('/bounded_controller/set_parameters',SetParameters,request)
        assert not rejected.results[0].successful
        record('reject_invalid_speed')
        start=position[0]; trigger('start')
        until(lambda:status[0].get('reason')=='distance_bound',30); spin(.6)
        moved=math.dist(start,position[0]); assert .4<moved<.6,moved
        assert base[0]==0.; record('clear_path_distance_bound',observed_displacement=moved)
        param('bounded_controller','max_distance',2.); param('bounded_controller','max_duration',30.)
        trigger('reset'); trigger('start'); until(lambda:status[0].get('reason')=='obstacle',35)
        spin(.5); assert status[0]['gap']<=.3 and base[0]==0.
        record('obstacle_stop',observed_position=position[0])
        rejected=call('/workshop/start',Trigger,Trigger.Request())
        assert not rejected.success
        record('latched_stop_requires_reset')
        # Move the obstacle out of the way with Gazebo's scene service. Never falsify scan clearance.
        import subprocess
        os.environ['GZ_IP']='127.0.0.1'; os.environ['GZ_PARTITION']='agentic_workshop'
        subprocess.run(['gz','service','-s','/world/workshop/set_pose','--reqtype','gz.msgs.Pose','--reptype','gz.msgs.Boolean','--timeout','5000','--req','name: "obstacle", position: {x: 4, y: 0, z: 0.25}'],check=True)
        until(lambda:status[0].get('gap') is not None and status[0]['gap']>.5,10)
        for mode in ('drop','invalid','missing_tf'):
            trigger('reset'); trigger('start'); until(lambda:base[0] is not None and base[0]>0)
            param('scan_relay','mode',mode); until(lambda:status[0].get('state')=='fault',10)
            spin(.5); p=position[0]; spin(.5)
            assert base[0]==0. and math.dist(p,position[0])<.03
            record('scan_'+mode,stopped_position=position[0]); param('scan_relay','mode','pass')
            until(lambda:status[0].get('gap') is not None,10)
        trigger('reset'); trigger('start'); until(lambda:base[0] is not None and base[0]>0)
        trigger('stop'); spin(.5); assert base[0]==0.; record('operator_stop')
        param('bounded_controller','max_duration',.5)
        trigger('reset'); trigger('start'); until(lambda:status[0].get('reason')=='time_bound',10)
        record('time_bound')
        param('bounded_controller','max_duration',30.)
        trigger('reset'); trigger('start'); until(lambda:base[0] is not None and base[0]>0)
        stopped_pid=int(status[0]['pid']); os.kill(stopped_pid,signal.SIGSTOP)
        spin(1.); p=position[0]; spin(.5)
        assert base[0]==0. and math.dist(p,position[0])<.03
        record('controller_process_loss_watchdog',stopped_position=position[0])
        os.kill(stopped_pid,signal.SIGCONT); stopped_pid=None
        trigger('stop')
    finally:
        if stopped_pid is not None: os.kill(stopped_pid,signal.SIGCONT)
        (out/'capstone-report.json').write_text(json.dumps({'provenance':'Gazebo TurtleBot3 Burger simulation','complete':len(results)==10,'results':results},indent=2))
        (out/'capstone-events.json').write_text(json.dumps(rows,indent=2))
        node.destroy_node(); rclpy.shutdown()
