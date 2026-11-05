import math
import json
import struct

def decode_cloud(msg):
    """Decode XYZ float fields using offsets, endian and both point/row strides."""
    if msg.width*msg.height>1000000 or msg.point_step<=0:
        raise ValueError('invalid size')
    if msg.row_step<msg.width*msg.point_step or len(msg.data)<msg.row_step*msg.height:
        raise ValueError('truncated buffer or invalid stride')
    fields={f.name:f for f in msg.fields}
    readers=[]
    for name in ('x','y','z'):
        f=fields[name]
        if f.count!=1 or f.datatype not in (7,8): raise ValueError('XYZ must be scalar floats')
        reader=struct.Struct(('>' if msg.is_bigendian else '<')+('f' if f.datatype==7 else 'd'))
        if f.offset<0 or f.offset+reader.size>msg.point_step: raise ValueError('field outside point')
        readers.append((reader,f.offset))
    return [tuple(reader.unpack_from(msg.data,row*msg.row_step+column*msg.point_step+offset)[0]
                  for reader,offset in readers)
            for row in range(msg.height) for column in range(msg.width)]

def stamp_seconds(stamp):
    return stamp.sec + stamp.nanosec * 1e-9

def transform_point(point, transform):
    x, y, z = map(float, point)
    q = transform.rotation
    # Quaternion rotation: v + 2*q.w*(q.xyz cross v) + 2*q.xyz cross(q.xyz cross v).
    uv = (q.y*z-q.z*y, q.z*x-q.x*z, q.x*y-q.y*x)
    uuv = (q.y*uv[2]-q.z*uv[1], q.z*uv[0]-q.x*uv[2], q.x*uv[1]-q.y*uv[0])
    t = transform.translation
    return tuple(v+2*q.w*a+2*b+d for v,a,b,d in zip((x,y,z),uv,uuv,(t.x,t.y,t.z)))

def publish_json(pub, **values):
    from std_msgs.msg import String
    pub.publish(String(data=json.dumps(values, allow_nan=False)))

def sector(points, threshold=.5, half_angle=30., z_min=.05, z_max=.5):
    distances = [math.hypot(x,y) for x,y,z in points
                 if all(math.isfinite(v) for v in (x,y,z)) and z_min <= z <= z_max
                 and abs(math.atan2(y,x)) <= math.radians(half_angle)]
    if not distances:
        return 'unknown', None, 0
    distance = min(distances)
    return ('blocked' if distance <= threshold else 'clear'), distance, len(distances)
