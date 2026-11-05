import importlib.util
import math
from pathlib import Path
import struct
from types import SimpleNamespace as NS
import unittest

path=Path(__file__).resolve().parents[1]/'agentic_workshop/common.py'
spec=importlib.util.spec_from_file_location('common',path)
common=importlib.util.module_from_spec(spec); spec.loader.exec_module(common)

class ContractTest(unittest.TestCase):
    def cloud(self,endian=False):
        return NS(width=1,height=2,point_step=32,row_step=40,is_bigendian=endian,
                  fields=[NS(name=n,offset=o,datatype=7,count=1) for n,o in [('x',0),('y',4),('z',8)]],
                  data=b''.join(struct.pack(('>' if endian else '<')+'fff20x',*p)+bytes(8)
                                for p in [(1.,2.,.2),(3.,4.,.3)]))
    def test_organized_row_padding_both_endians(self):
        for endian in (False,True):
            points=common.decode_cloud(self.cloud(endian))
            self.assertEqual([p[:2] for p in points],[(1.,2.),(3.,4.)])
    def test_truncation(self):
        msg=self.cloud(); msg.data=msg.data[:-1]
        with self.assertRaises(ValueError): common.decode_cloud(msg)
    def test_bad_field(self):
        msg=self.cloud(); msg.fields[0].offset=31
        with self.assertRaises(ValueError): common.decode_cloud(msg)
    def test_side_and_front(self):
        self.assertEqual(common.sector([(0,.2,.2),(1,0,.2)]),('clear',1.,1))
        self.assertEqual(common.sector([(.5,0,.2)]),('blocked',.5,1))
    def test_no_usable_points(self):
        for points in ([],[(math.nan,0,.2)],[(.1,0,0)],[(-1,0,.2)]):
            self.assertEqual(common.sector(points),('unknown',None,0))
    def test_rotation_and_translation(self):
        tf=NS(rotation=NS(x=0,y=0,z=math.sqrt(.5),w=math.sqrt(.5)),translation=NS(x=1,y=2,z=3))
        point=common.transform_point((1,0,0),tf)
        for a,b in zip(point,(1,3,3)): self.assertAlmostEqual(a,b)

if __name__=='__main__': unittest.main()
