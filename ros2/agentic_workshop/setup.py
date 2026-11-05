from setuptools import setup
from glob import glob
setup(name='agentic_workshop', version='0.1.0', packages=['agentic_workshop'], tests_require=['pytest'],
      data_files=[('share/ament_index/resource_index/packages', ['resource/agentic_workshop']),
                  ('share/agentic_workshop', ['package.xml']),
                  ('share/agentic_workshop/launch', glob('launch/*.py')),
                  ('share/agentic_workshop/worlds', glob('worlds/*'))],
      entry_points={'console_scripts': [
          'cloud_diagnostic = agentic_workshop.cloud:main',
          'scan_relay = agentic_workshop.relay:main',
          'command_guard = agentic_workshop.guard:main',
          'bounded_controller = agentic_workshop.controller:main',
          'replay_demo = agentic_workshop.replay_demo:main',
          'capstone_check = agentic_workshop.capstone_check:main']})
