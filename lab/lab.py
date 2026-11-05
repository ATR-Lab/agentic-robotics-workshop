"""Step runner and doctor for the one-hour hands-on lab.

Usage: python3 -I lab/lab.py STEP [run|doctor|help|clean]
The shell scripts in lab/ call this file; Windows without Bash can call it directly.
Standard library only, Python 3.9+. Steps 03 and 04 need ROS 2: on a computer with Docker they run in
the station container (lab/docker/Dockerfile); on a prepared Linux station they run directly.
"""
import datetime
import json
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
# Never crash on a character the terminal cannot show (a Windows code page, for example).
for _stream in (sys.stdout, sys.stderr):
    _stream.reconfigure(errors='replace')

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / 'runs'
BASELINE_TAG = 'lab-baseline'
ROS_DISTRO = os.environ.get('LAB_ROS_DISTRO', 'jazzy')
ROS_WS = Path(os.environ.get('LAB_ROS_WS', Path.home() / 'ros_ws')).expanduser()
LEFTOVER_PATTERN = ('gz sim|ros_gz_bridge|parameter_bridge|robot_state_publisher|lib/agentic_workshop/'
                    '|ros2 (launch|run) agentic_workshop|ros2 bag play')
IMAGE = os.environ.get('LAB_IMAGE', 'ghcr.io/atr-lab/agentic-workshop-station:2026.11')
BUILD_COMMAND = f'docker build -t {IMAGE} -f lab/docker/Dockerfile .'
COLOR = sys.stdout.isatty() and os.environ.get('NO_COLOR') is None and os.name != 'nt'


def paint(text, code):
    return f'\033[{code}m{text}\033[0m' if COLOR else text


class Doctor:
    """Collects PASS/WARN/FAIL lines; every problem line carries a fix."""

    def __init__(self, title):
        self.title, self.lines, self.failed = title, [], False
        print(paint(f'\n== {title}', '1'))

    def ok(self, what):
        self._emit('PASS', what, None, '32')

    def info(self, what):
        self._emit('INFO', what, None, '36')

    def warn(self, what, fix):
        self._emit('WARN', what, fix, '33')

    def fail(self, what, fix):
        self.failed = True
        self._emit('FAIL', what, fix, '31')

    def _emit(self, level, what, fix, code):
        self.lines.append((level, what, fix))
        print(f'{paint(level, code)}  {what}')
        if fix:
            print(f'      Fix: {fix}')


def read(path):
    """Text of a file as UTF-8, whatever the platform's default encoding is."""
    return Path(path).read_text(encoding='utf-8', errors='replace')


def sh(args, timeout=30, env=None, cwd=ROOT):
    """Run a command and return (exit code, combined output); never raises."""
    try:
        done = subprocess.run(args, cwd=cwd, env=env, timeout=timeout, text=True, encoding='utf-8', errors='replace',
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return done.returncode, done.stdout.rstrip()
    except FileNotFoundError:
        return 127, f'{args[0]}: command not found'
    except subprocess.TimeoutExpired:
        return 124, f'timed out after {timeout} s'


def show(args):
    print(paint('$ ' + ' '.join(str(a) for a in args), '2'))


def git(*args, timeout=30):
    return sh(['git', '-C', str(ROOT), *args], timeout=timeout)


def stamp():
    return datetime.datetime.now().strftime('%Y%m%d-%H%M%S')


def save_result(step, outcome, summary, commands, evidence, artifacts=()):
    folder = RUNS / step
    folder.mkdir(parents=True, exist_ok=True)
    result = {'step': step, 'outcome': outcome, 'summary': summary, 'commands': commands,
              'evidence': evidence, 'artifacts': [str(a) for a in artifacts],
              'finished': datetime.datetime.now().isoformat(timespec='seconds'),
              'host': platform.node()}
    (folder / 'latest.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


def latest(step):
    path = RUNS / step / 'latest.json'
    return json.loads(read(path)) if path.exists() else None


# ---------------------------------------------------------------- shared checks

def check_python(doc):
    version = '.'.join(map(str, sys.version_info[:3]))
    if sys.version_info < (3, 9):
        doc.fail(f'Python {version} is older than 3.9', 'install Python 3.9 or newer')
    else:
        doc.ok(f'Python {version} at {sys.executable}')


def check_platform(doc):
    system = platform.system()
    if system == 'Windows':
        if os.environ.get('MSYSTEM'):
            doc.ok(f'Windows with Git Bash ({os.environ["MSYSTEM"]})')
        else:
            doc.warn('Windows without Bash: the .sh wrappers need Git Bash or WSL',
                     'run the same step as  py -3 lab\\lab.py 01 run  (any step number works)')
    elif 'microsoft' in platform.release().lower():
        doc.ok('Linux on WSL')
        if str(ROOT).startswith('/mnt/'):
            doc.warn('the workshop folder is on the Windows drive (/mnt/...), which makes Git slow in WSL',
                     'copy it into your WSL home, for example  cp -r "$PWD" ~/agentic-lab')
    else:
        doc.ok(f'{system} {platform.release()} ({platform.machine()})')


def check_folder(doc):
    synced = re.search(r'OneDrive|iCloud|Mobile Documents|Dropbox|Google Drive', str(ROOT))
    if synced:
        doc.warn(f'the workshop folder is inside a synced folder ({synced.group(0)}); sync can lock Git files',
                 'copy the folder somewhere local, such as your home folder, and work there')
    try:
        RUNS.mkdir(exist_ok=True)
        probe = RUNS / '.write-test'
        probe.write_text('ok', encoding='utf-8')
        probe.unlink()
        doc.ok(f'can write results to {RUNS}')
    except OSError as error:
        doc.fail(f'cannot write to {RUNS}: {error}',
                 'unzip or copy the workshop into a folder you own, such as your home folder')
    free = shutil.disk_usage(ROOT).free / 2**30
    if free < 1:
        doc.warn(f'only {free:.1f} GB free on this disk', 'free at least 1 GB')


def check_git(doc):
    code, out = sh(['git', '--version'])
    if code:
        fix = ('run  xcode-select --install  and accept the prompt' if platform.system() == 'Darwin'
               else 'install Git (git-scm.com) and open a new terminal')
        doc.fail('Git is not installed or not working', fix)
        return False
    doc.ok(out)
    if git('config', 'user.email')[0]:
        doc.warn('Git has no user.email; the lab will commit as "Workshop participant"',
                 'optional:  git config --global user.name "Your Name"  and  git config --global user.email you@example.com')
    return True


def repo_state():
    """Return 'none', 'nested', 'empty' or 'ready' for the workshop folder's Git state."""
    code, top = git('rev-parse', '--show-toplevel')
    if code:
        return 'none'
    if Path(top).resolve() != ROOT:
        return 'nested'
    return 'ready' if git('rev-parse', '--verify', '-q', 'HEAD')[0] == 0 else 'empty'


def check_agents(doc):
    found = [name for name in ('claude', 'codex') if shutil.which(name)]
    if found:
        doc.ok('coding agent CLI on PATH: ' + ', '.join(found))
    else:
        doc.warn('no claude or codex command on PATH',
                 'the desktop or IDE app works too; check you are signed in. No access: pair with a neighbour')


def check_exercise_files(doc):
    missing = [p for p in ('exercises/check.py', 'exercises/clearance.py', 'templates/run-report.md')
               if not (ROOT / p).exists()]
    if missing:
        doc.fail('missing workshop files: ' + ', '.join(missing), 'get a fresh copy of the workshop folder')
        return False
    try:
        compile(read(ROOT / 'exercises/clearance.py'), 'exercises/clearance.py', 'exec')
        doc.ok('exercises/clearance.py parses')
    except SyntaxError as error:
        doc.fail(f'exercises/clearance.py has a syntax error on line {error.lineno}: {error.msg}',
                 'ask your agent to fix the syntax error, or see the diff with  git diff ' + BASELINE_TAG)
    return True


def run_checker():
    args = [sys.executable, '-I', 'exercises/check.py']
    show(['python3', '-I', 'exercises/check.py'])
    code, out = sh(args, timeout=60)
    print(out)
    match = re.search(r'(\d+)/(\d+) passed', out)
    return code, out, (int(match.group(1)), int(match.group(2))) if match else None


# ---------------------------------------------------------------- ROS station checks

def ros_env(domain):
    env = dict(os.environ, ROS_DOMAIN_ID=str(domain), PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONSTARTUP', None)
    return env


def ros(args, domain, timeout=30):
    """Run a command inside a shell that has sourced ROS and the workshop workspace."""
    script = (f'source /opt/ros/{ROS_DISTRO}/setup.bash && source "{ROS_WS}/install/setup.bash" && exec "$@"')
    return sh(['bash', '-c', script, 'lab', *args], timeout=timeout, env=ros_env(domain))


def domain_for(step):
    default = 77 if step == '03' else 78
    raw = os.environ.get('LAB_DOMAIN_ID', str(default))
    return int(raw) if raw.isdigit() else -1


def ancestors():
    """This process and its parents, which must never count as leftovers."""
    pids, pid = set(), os.getpid()
    while pid > 1 and pid not in pids:
        pids.add(pid)
        try:
            pid = int(read(f'/proc/{pid}/stat').rsplit(')', 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            break
    return pids


def leftovers():
    """Lines of 'PID command' for this user's replay or simulator processes."""
    code, out = sh(['pgrep', '-a', '-u', str(os.getuid()), '-f', LEFTOVER_PATTERN])
    mine = ancestors()
    return [line for line in out.splitlines() if line and int(line.split()[0]) not in mine] if code == 0 else []


def native_ros():
    return platform.system() == 'Linux' and Path(f'/opt/ros/{ROS_DISTRO}/setup.bash').exists()


def station_route():
    """'native' runs the ROS steps on this machine; 'docker' runs them in the station container."""
    chosen = os.environ.get('LAB_STATION', 'auto')
    if chosen in ('native', 'docker'):
        return chosen
    return 'native' if native_ros() or not shutil.which('docker') else 'docker'


def check_station(doc, step, need_sim=False):
    if platform.system() != 'Linux':
        doc.fail(f'step {step} needs ROS 2, which runs here only through Docker, and the docker command was not found',
                 'install Docker Desktop (or OrbStack on a Mac), start it and run this step again; or use your '
                 'assigned station, or the saved reports in evidence/2026-11-03/ and mark the step unexecuted')
        return False
    os_release = read('/etc/os-release') if Path('/etc/os-release').exists() else ''
    if 'VERSION_CODENAME=noble' in os_release:
        doc.ok('Ubuntu 24.04 (noble)')
    else:
        doc.warn('not Ubuntu 24.04; the lab was verified on Ubuntu 24.04 with ROS 2 Jazzy',
                 'use the prepared station image if anything below fails')
    if not Path(f'/opt/ros/{ROS_DISTRO}/setup.bash').exists():
        others = sorted(p.parent.name for p in Path('/opt/ros').glob('*/setup.bash'))
        doc.fail(f'ROS 2 {ROS_DISTRO} is not installed in /opt/ros/{ROS_DISTRO}',
                 f'installed distributions: {", ".join(others) or "none"}. Use the prepared station, or set '
                 'LAB_ROS_DISTRO to an installed one (untested)')
        return False
    doc.ok(f'ROS 2 {ROS_DISTRO} found')
    if os.environ.get('ROS_DISTRO') not in (None, ROS_DISTRO):
        doc.warn(f'this shell already sourced ROS {os.environ["ROS_DISTRO"]}', 'open a fresh terminal')
    for var in ('CONDA_PREFIX', 'VIRTUAL_ENV'):
        if os.environ.get(var):
            doc.warn(f'{var} is set; ROS {ROS_DISTRO} needs the system Python',
                     'run  conda deactivate  (or  deactivate  for a venv) and try again')
    if not (ROS_WS / 'install/setup.bash').exists():
        doc.fail(f'the workshop ROS workspace is not built ({ROS_WS}/install/setup.bash is missing)',
                 'run  bash scripts/boat-build.sh  on the station, or set LAB_ROS_WS to the built workspace')
        return False
    domain = domain_for(step)
    if not 0 <= domain <= 101:
        doc.fail(f'LAB_DOMAIN_ID={os.environ.get("LAB_DOMAIN_ID")} is not a number from 0 to 101',
                 'unset it, or pick a number from 0 to 101 that no other station uses')
        return False
    packages = ['agentic_workshop'] + (['turtlebot3_gazebo'] if need_sim else [])
    for package in packages:
        code, out = ros(['ros2', 'pkg', 'prefix', package], domain)
        if code:
            doc.fail(f'ROS package {package} is not available in the sourced workspace',
                     'rebuild with  bash scripts/boat-build.sh  and check its output for errors')
            return False
        doc.ok(f'{package} at {out.splitlines()[-1]}')
    code, out = ros(['python3', '-c', 'import rclpy, sensor_msgs_py, rosbag2_py'], domain)
    if code:
        doc.fail('ROS Python modules do not import: ' + out.splitlines()[-1][:160],
                 'deactivate conda/venv, open a fresh terminal, and check the station image')
        return False
    doc.ok('rclpy, sensor_msgs_py and rosbag2_py import')
    if need_sim:
        code, out = sh(['bash', '-c', f'source /opt/ros/{ROS_DISTRO}/setup.bash && gz sim --versions'], timeout=30)
        if code:
            doc.fail('Gazebo (gz sim) does not run: ' + out[:160], 'install ros-jazzy-ros-gz (see scripts/boat-setup.sh)')
            return False
        doc.ok('Gazebo ' + out.splitlines()[-1])
        try:
            memory = int(re.search(r'MemTotal:\s+(\d+)', read('/proc/meminfo')).group(1)) / 2**20
            if memory < 3.5:
                doc.warn(f'only {memory:.1f} GB of memory; Gazebo may be slow or killed', 'close other programs')
        except (OSError, AttributeError):
            pass
    busy = leftovers()
    if busy:
        doc.fail('earlier replay or simulator processes are still running:\n      ' + '\n      '.join(busy[:6]),
                 f'run  bash lab/{SCRIPTS[step]} clean')
        return False
    doc.ok('no leftover replay or simulator processes')
    code, out = ros(['ros2', 'node', 'list', '--no-daemon', '--spin-time', '3'], domain, timeout=30)
    nodes = [n for n in out.splitlines() if n.startswith('/')] if code == 0 else []
    if nodes:
        doc.fail(f'ROS domain {domain} already has nodes ({", ".join(nodes[:4])}); another station or run is using it',
                 f'pick an unused domain, for example  LAB_DOMAIN_ID={domain + 10} bash lab/{SCRIPTS[step]}')
        return False
    doc.ok(f'ROS domain {domain} is free')
    return True


def clean(step):
    if station_route() == 'docker':
        return clean_container(step)
    busy = leftovers()
    if not busy:
        print('Nothing to clean: no replay or simulator processes are running for this user.')
        return 0
    print('Stopping these processes:\n  ' + '\n  '.join(busy))
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGKILL):
        for line in leftovers():
            try:
                os.kill(int(line.split()[0]), sig)
            except ProcessLookupError:
                pass
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline and leftovers():
            time.sleep(.5)
        if not leftovers():
            print('Stopped. Run the step again.')
            return 0
    print('Some processes are still running; ask a facilitator.')
    return 1


# ---------------------------------------------------------------- Docker station

def container_name(step):
    return f'atr-lab-{step}'


def running_containers():
    code, out = sh(['docker', 'ps', '--format', '{{.Names}}', '--filter', 'name=^atr-lab-0[34]$'])
    return out.split() if code == 0 else []


def check_docker(doc, step, need_sim=False):
    code, out = sh(['docker', 'version', '--format', '{{.Server.Os}}/{{.Server.Arch}}'], timeout=30)
    if code == 127:
        doc.fail('the docker command was not found',
                 'install Docker Desktop (Windows or macOS) or Docker Engine (Linux) and open a new terminal')
        return False
    if code:
        if 'permission denied' in out.lower():
            doc.fail('Docker is running but this user may not use it (permission denied)',
                     'run  sudo usermod -aG docker $USER , then log out and back in')
        else:
            start = {'Darwin': 'start Docker Desktop or OrbStack', 'Windows': 'start Docker Desktop',
                     'Linux': 'run  sudo systemctl start docker'}.get(platform.system(), 'start Docker')
            doc.fail('Docker is installed but its engine is not running: ' + out.splitlines()[-1][:120],
                     f'{start}, wait until it reports that it is running, then try again')
        return False
    engine_arch = out.split('/')[-1]
    doc.ok(f'Docker engine running ({out})')
    code, out = sh(['docker', 'image', 'inspect', '--format', '{{.Architecture}} {{.Size}}', IMAGE])
    if code:
        doc.fail(f'the station image {IMAGE} is not on this computer',
                 f'run  docker pull {IMAGE}  (about 1.2 GB; do it before the workshop). Offline: load the file a '
                 f'facilitator gives you with  docker load -i <file> , or build it:  {BUILD_COMMAND}')
        return False
    image_arch, size = out.split()
    doc.ok(f'station image {IMAGE} ({image_arch}, {int(size) / 1e9:.1f} GB)')
    if image_arch != engine_arch:
        doc.warn(f'the image is built for {image_arch} but Docker runs {engine_arch}; it will be slow under emulation',
                 f'run  docker pull {IMAGE}  again; it fetches the version for this computer')
    if need_sim:
        code, out = sh(['docker', 'info', '--format', '{{.MemTotal}}'])
        if code == 0 and out.isdigit() and int(out) / 2**30 < 3.5:
            doc.warn(f'Docker may use only {int(out) / 2**30:.1f} GB of memory; Gazebo may be slow or killed',
                     'raise the memory limit to 4 GB or more (Docker Desktop: Settings > Resources)')
    busy = running_containers()
    if busy:
        doc.fail('an earlier lab container is still running: ' + ', '.join(busy),
                 f'run  bash lab/{SCRIPTS[step]} clean')
        return False
    doc.ok('no lab container is running')
    return True


def host_timezone():
    """This computer's current UTC offset as a POSIX TZ value, so result folders get local times."""
    east = time.localtime().tm_gmtoff // 60
    hours, minutes = divmod(abs(east), 60)
    sign = '-' if east < 0 else '+'
    return f'<{sign}{hours:02d}{minutes:02d}>{"-" if east > 0 else ""}{hours}:{minutes:02d}'


def docker_command(step, action, interactive=False):
    """The docker run command that performs a step inside the station container on this folder."""
    command = ['docker', 'run', '--rm', '--init', '--name', container_name(step), '--hostname', 'docker-station',
               '--shm-size', '1g', '--mount', f'type=bind,source={ROOT},target=/home/user/workshop',
               '-e', f'TZ={host_timezone()}', '-e', 'PYTHONUNBUFFERED=1']
    if interactive:
        command.append('-it')
    for var in ('LAB_DOMAIN_ID', 'LAB_LAUNCH_TIMEOUT', 'NO_COLOR'):
        if var in os.environ:
            command += ['-e', f'{var}={os.environ[var]}']
    if platform.system() == 'Linux':
        # Write results as this user. Rootless Docker already maps the container's root to this user.
        rootless = 'rootless' in sh(['docker', 'info', '--format', '{{.SecurityOptions}}'])[1]
        command += ['--user', '0:0' if rootless else f'{os.getuid()}:{os.getgid()}', '-e', 'HOME=/tmp']
    return command + [IMAGE, 'python3', '-I', 'lab/lab.py', step, action]


def doctor_in_docker(doc, step, need_sim):
    if not check_docker(doc, step, need_sim):
        return
    command = docker_command(step, 'doctor')
    show(command)
    code, out = sh(command, timeout=180)
    print('\n'.join('  | ' + line for line in out.splitlines()))
    if code:
        doc.fail('the doctor inside the station container failed (its lines are marked | above)',
                 f'follow its Fix lines; if the workshop package changed, rebuild the image:  {BUILD_COMMAND}')
    else:
        doc.ok('the station container passes its own doctor')


def run_in_docker(step, name, need_sim):
    doc = Doctor(f'{step} {name} · doctor (Docker station)')
    if not check_docker(doc, step, need_sim):
        return 1
    print(paint(f'\n== {step} {name} · run in the station container', '1'))
    command = docker_command(step, 'run', interactive=sys.stdin.isatty() and sys.stdout.isatty())
    show(command)
    sys.stdout.flush()
    process = subprocess.Popen(command, cwd=ROOT)
    try:
        return process.wait()
    except KeyboardInterrupt:
        # Docker passes Ctrl-C to the step in the container, which stops its own processes first.
        try:
            process.wait(timeout=45)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            pass
        sh(['docker', 'rm', '-f', container_name(step)])
        return 130


def clean_container(step):
    busy = running_containers()
    if not busy:
        print('Nothing to clean: no lab container is running.')
        return 0
    show(['docker', 'rm', '-f', *busy])
    code, out = sh(['docker', 'rm', '-f', *busy], timeout=60)
    print(out)
    print('Stopped. Run the step again.' if code == 0 else 'Docker could not remove them; ask a facilitator.')
    return code


# ---------------------------------------------------------------- steps

def doctor_check(step):
    doc = Doctor('00 check · whole-lab doctor')
    check_platform(doc)
    check_python(doc)
    check_folder(doc)
    if check_git(doc):
        state = repo_state()
        doc.info({'none': 'not a Git repository yet; step 01 creates the baseline commit',
                  'nested': 'inside another Git repository; step 01 makes this folder its own repository',
                  'empty': 'a Git repository with no commits (see step 01 doctor)',
                  'ready': 'Git repository with commits'}[state])
    check_agents(doc)
    route = station_route()
    if route == 'docker':
        doc.info('Docker found: steps 03 and 04 run in the station container; checking it')
    elif native_ros():
        doc.info('ROS 2 station detected; checking steps 03 and 04')
    else:
        doc.warn('no Docker and no ROS 2 here, so steps 03 and 04 cannot run on this machine',
                 'install Docker Desktop (or OrbStack on a Mac) before the lab, or use an assigned station')
    results = [doc, doctor_reproduce('01', quiet=True)]
    if route == 'docker':
        results.append(doctor_simulate('04'))
    elif native_ros():
        results += [doctor_replay('03'), doctor_simulate('04')]
    report = RUNS / f'doctor-{stamp()}.txt'
    RUNS.mkdir(exist_ok=True)
    lines = [f'Lab doctor report {datetime.datetime.now().isoformat(timespec="seconds")}',
             f'host={platform.node()} os={platform.platform()} python={sys.version.split()[0]} folder={ROOT}',
             f'shell={os.environ.get("SHELL") or os.environ.get("ComSpec", "?")} station={route} image={IMAGE} '
             f'ros_ws={ROS_WS} ros_distro={ROS_DISTRO}']
    for d in results:
        lines.append(f'\n[{d.title}]')
        lines += [f'{level} {what}' + (f'\n  fix: {fix}' if fix else '') for level, what, fix in d.lines]
    report.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    failed = any(d.failed for d in results)
    print(f'\nSaved {report.relative_to(ROOT)}. ' +
          ('Show it to a facilitator if a FAIL line is unclear.' if failed else 'Ready for step 01.'))
    return int(failed)


def doctor_reproduce(step, quiet=False):
    doc = Doctor('01 reproduce · doctor')
    if not quiet:
        check_python(doc)
        check_folder(doc)
        if not check_git(doc):
            return doc
    if not check_exercise_files(doc):
        return doc
    state = repo_state()
    if state == 'empty':
        doc.fail('this folder is a Git repository with no commits, so there is no baseline to compare against',
                 'if this is your own copy, run  git add -A && git commit -m baseline  and run step 01 again. '
                 "If it is the organizer's master copy, copy the folder first (cp -R) and work in the copy")
    elif state == 'nested':
        doc.warn('this folder sits inside another Git repository',
                 'step 01 will make it a repository of its own, so your changes stay separate')
    elif state == 'ready' and git('rev-parse', '-q', '--verify', BASELINE_TAG)[0]:
        doc.info(f'no {BASELINE_TAG} tag yet; step 01 marks the current commit as your baseline')
    else:
        doc.ok('baseline ready' if state == 'ready' else 'step 01 will create the baseline commit')
    return doc


def make_baseline():
    state = repo_state()
    identity = ['-c', 'user.name=Workshop participant', '-c', 'user.email=participant@workshop.invalid']
    if git('config', 'user.email')[0] == 0:
        identity = []
    if state == 'empty':
        return None
    if state in ('none', 'nested'):
        show(['git', 'init'])
        sh(['git', 'init', '-q'], cwd=ROOT)
        git('add', '-A')
        show(['git', 'commit', '-m', 'lab baseline'])
        code, out = sh(['git', *identity, 'commit', '-q', '-m', 'lab baseline'], cwd=ROOT)
        if code:
            print(out)
            return None
    if git('rev-parse', '-q', '--verify', BASELINE_TAG)[0]:
        show(['git', 'tag', BASELINE_TAG])
        git('tag', BASELINE_TAG)
    return git('rev-parse', '--short', BASELINE_TAG)[1]


def run_reproduce(step):
    doc = doctor_reproduce(step)
    if doc.failed:
        return 1
    print(paint('\n== 01 reproduce · run', '1'))
    baseline = make_baseline()
    if not baseline:
        print('FAIL  could not create the baseline commit; run  bash lab/01-reproduce.sh doctor')
        return 1
    print(f'Baseline: {BASELINE_TAG} = {baseline}. Later, see your change with  git diff {BASELINE_TAG}')
    code, out, score = run_checker()
    out_file = RUNS / '01-reproduce' / f'{stamp()}.txt'
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(out + '\n', encoding='utf-8')
    if score and score[0] < score[1]:
        outcome = 'expected-fail'
        summary = f'starter fails as expected: {score[0]}/{score[1]} checks pass'
        print(paint(f'\nAs expected, the starter fails ({score[0]}/{score[1]}).', '32'))
        print('Before editing, write down which FAIL surprised you and why a valid point can still give the wrong answer.')
    elif score:
        outcome, summary = 'already-passing', f'starter already passes {score[0]}/{score[1]}; the file was changed'
        print(paint('\nThe starter already passes, so exercises/clearance.py has been changed.', '33'))
        print('If that was not you, get a fresh copy; otherwise continue with step 02.')
    else:
        outcome = 'error'
        summary = 'the checker did not run: ' + (out.splitlines()[-1][:120] if out else 'no output')
        print(paint('\nThe checker did not run. Run  bash lab/01-reproduce.sh doctor', '31'))
    save_result('01-reproduce', outcome, summary, ['python3 -I exercises/check.py'],
                'authored offline fixtures', [out_file.relative_to(ROOT)])
    return 0 if outcome in ('expected-fail', 'already-passing') else 1


def doctor_repair(step):
    doc = Doctor('02 repair · doctor')
    check_python(doc)
    check_agents(doc)
    if not check_exercise_files(doc) or not check_git(doc):
        return doc
    if git('rev-parse', '-q', '--verify', BASELINE_TAG)[0]:
        doc.fail('no baseline yet, so your change cannot be shown as a diff', 'run  bash lab/01-reproduce.sh  first')
        return doc
    if git('diff', '--quiet', BASELINE_TAG, '--', 'exercises/check.py')[0]:
        doc.fail('exercises/check.py differs from the baseline; the evidence would change with the code',
                 f'restore it with  git checkout {BASELINE_TAG} -- exercises/check.py  and add new cases in a separate file')
    else:
        doc.ok('exercises/check.py is unchanged since the baseline')
    changed = changed_files()
    others = [f for f in changed if f != 'exercises/clearance.py']
    if others:
        doc.warn('files other than exercises/clearance.py changed: ' + ', '.join(others[:6]),
                 'check each one is intended; the task needs only a narrow change to clearance.py')
    if 'exercises/clearance.py' in changed:
        doc.ok('exercises/clearance.py has changed since the baseline')
    else:
        doc.info('exercises/clearance.py has not changed yet')
    return doc


def changed_files():
    _, tracked = git('diff', '--name-only', BASELINE_TAG)
    _, untracked = git('ls-files', '--others', '--exclude-standard')
    return [f for f in (tracked.splitlines() + untracked.splitlines()) if f]


def run_repair(step):
    doc = doctor_repair(step)
    if doc.failed:
        return 1
    print(paint('\n== 02 repair · run', '1'))
    code, out, score = run_checker()
    show(['git', 'diff', '--stat', BASELINE_TAG])
    print(git('diff', '--stat', BASELINE_TAG)[1] or '(no changes yet)')
    show(['git', 'diff', BASELINE_TAG, '--', 'exercises/clearance.py'])
    print(git('--no-pager', 'diff', BASELINE_TAG, '--', 'exercises/clearance.py')[1] or '(no changes yet)')
    out_file = RUNS / '02-repair' / f'{stamp()}.txt'
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(out + '\n\n' + git('diff', BASELINE_TAG)[1] + '\n', encoding='utf-8')
    passed = bool(score) and score[0] == score[1]
    summary = f'{score[0]}/{score[1]} checks pass' if score else 'checker did not run'
    if passed:
        print(paint(f'\nAll {score[1]} checks pass.', '32') + ' Now explain it back before moving on:')
        print('  1. Trace the side point (0, 0.20, 0.20) through your code: why is it ignored now?')
        print('  2. Predict, then test: a point exactly at 0.50 m; only ground points; a failed transform.')
        print('  3. Ask a second agent conversation to review the diff against the contract.')
    else:
        print(paint(f'\nNot done yet: {summary}.', '33') + ' Read the FAIL lines, ask your agent to explain them, and run this again.')
    save_result('02-repair', 'pass' if passed else 'fail', summary,
                ['python3 -I exercises/check.py', f'git diff {BASELINE_TAG}'],
                'authored offline fixtures', [out_file.relative_to(ROOT)])
    return 0 if passed else 1


def doctor_replay(step):
    if station_route() == 'docker':
        doc = Doctor('03 replay · doctor (Docker station)')
        doctor_in_docker(doc, step, need_sim=False)
        return doc
    doc = Doctor('03 replay · doctor (ROS 2 station)')
    check_station(doc, step)
    return doc


def run_ros_step(step, name, args, timeout, report_name, summarize, prepare=None):
    doc = doctor_replay(step) if step == '03' else doctor_simulate(step)
    if doc.failed:
        return 1
    print(paint(f'\n== {step} {name} · run', '1'))
    domain = domain_for(step)
    out = RUNS / f'{step}-{name}' / stamp()
    out.parent.mkdir(parents=True, exist_ok=True)
    background = prepare(domain, out) if prepare else None
    if prepare and background is None:
        return 1
    try:
        command = [*args, '--output', str(out)]
        show([f'ROS_DOMAIN_ID={domain}', *command])
        started = time.monotonic()
        code, text = ros(command, domain, timeout=timeout)
        print(text[-4000:])
        print(f'(finished in {time.monotonic() - started:.0f} s, exit {code})')
    finally:
        if background:
            stop_background(background)
    report = out / report_name
    if not report.exists():
        print(paint(f'\nNo {report_name} was written.', '31') +
              f' Run  bash lab/{SCRIPTS[step]} doctor ; the full output is above.')
        save_result(f'{step}-{name}', 'error', f'no report (exit {code})', [' '.join(command)], '', [])
        return 1
    passed, summary = summarize(json.loads(read(report)), code)
    evidence = ('authored synthetic PointCloud2 bag replayed through ROS 2' if step == '03'
                else 'Gazebo TurtleBot3 Burger simulation (headless)')
    save_result(f'{step}-{name}', 'pass' if passed else 'fail', summary, [' '.join(command)], evidence,
                [p.relative_to(ROOT) for p in sorted(out.iterdir())])
    print(paint(f'\n{summary}', '32' if passed else '31'))
    print(f'Report: {report.relative_to(ROOT)}')
    return 0 if passed else 1


def summarize_replay(report, code):
    checks = report.get('checks', {})
    for name, check in checks.items():
        label = f'phase {name}' if name.isdigit() else name
        detail = f" expected {check['expected']}, saw {check['seen']}" if 'expected' in check else ''
        print(f"  {'PASS' if check.get('pass') else 'FAIL'} {label}{detail}")
    passed_count = sum(bool(c.get('pass')) for c in checks.values())
    passed = code == 0 and checks and passed_count == len(checks)
    return passed, f'replay: {passed_count}/{len(checks)} checks pass ({report.get("messages", "?")} messages)'


def run_replay(step):
    if station_route() == 'docker':
        return run_in_docker(step, 'replay', need_sim=False)
    return run_ros_step(step, 'replay', ['ros2', 'run', 'agentic_workshop', 'replay_demo'], 180,
                        'replay-report.json', summarize_replay)


def doctor_simulate(step):
    if station_route() == 'docker':
        doc = Doctor('04 simulate · doctor (Docker station)')
        doctor_in_docker(doc, step, need_sim=True)
        return doc
    doc = Doctor('04 simulate · doctor (ROS 2 station)')
    check_station(doc, step, need_sim=True)
    return doc


def start_capstone(domain, out):
    log = out / 'launch.log'
    out.mkdir(parents=True, exist_ok=True)
    command = ['ros2', 'launch', 'agentic_workshop', 'capstone.launch.py']
    show([f'ROS_DOMAIN_ID={domain}', *command, f'> {log.relative_to(ROOT)}'])
    script = f'source /opt/ros/{ROS_DISTRO}/setup.bash && source "{ROS_WS}/install/setup.bash" && exec "$@"'
    handle = log.open('w', encoding='utf-8')
    process = subprocess.Popen(['bash', '-c', script, 'lab', *command], cwd=ROOT, env=ros_env(domain),
                               stdout=handle, stderr=subprocess.STDOUT, start_new_session=True)
    limit = int(os.environ.get('LAB_LAUNCH_TIMEOUT', '120'))
    print(f'Waiting up to {limit} s for the simulated robot to come up...')
    deadline = time.monotonic() + limit
    try:
        while time.monotonic() < deadline:
            if process.poll() is not None:
                break
            code, services = ros(['ros2', 'service', 'list', '--no-daemon', '--spin-time', '2'], domain, timeout=30)
            if '/workshop/start' in services.split():
                print('Simulator and controller are up.')
                return process, handle
            time.sleep(3)
    except KeyboardInterrupt:
        # The launch runs in its own session, so Ctrl-C does not reach it.
        print('\nStopping the simulator...')
        stop_background((process, handle))
        raise
    handle.flush()
    tail = read(log).splitlines()[-25:]
    reason = 'the launch exited early' if process.poll() is not None else f'it was not ready after {limit} s'
    print(paint(f'\nThe simulator did not start: {reason}. Last lines of {log.relative_to(ROOT)}:', '31'))
    print('\n'.join(tail))
    print('Common causes: leftover processes (run  bash lab/04-simulate.sh clean), a domain shared with another '
          'station (set LAB_DOMAIN_ID), or too little memory. Raise LAB_LAUNCH_TIMEOUT on a slow machine.')
    stop_background((process, handle))
    return None


def group_alive(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False


def stop_background(background):
    """Stop the launch and everything in its process group, escalating to SIGKILL.

    Gazebo's server can outlive the launch process during start-up, so wait for the
    whole group rather than for the launch process alone.
    """
    process, handle = background
    for sig, wait in ((signal.SIGINT, 15), (signal.SIGTERM, 5), (signal.SIGKILL, 5)):
        process.poll()
        if not group_alive(process.pid):
            break
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            break
        deadline = time.monotonic() + wait
        while time.monotonic() < deadline and group_alive(process.pid):
            process.poll()
            time.sleep(.2)
    handle.close()
    if leftovers():
        print(paint('Some simulator processes are still running;', '33') + ' run  bash lab/04-simulate.sh clean')


def summarize_capstone(report, code):
    results = report.get('results', [])
    for result in results:
        status = result.get('status', {})
        if status.get('state') in ('idle', 'stopped', 'fault'):
            detail = f"reason: {status.get('reason')}"
        elif 'watchdog' in result.get('scenario', ''):
            detail = 'controller suspended mid-run; the independent command guard sent zero'
        else:
            detail = f"last controller state: {status.get('state')}"
        print(f"  {'PASS' if result.get('pass') else 'FAIL'} {result.get('scenario')} ({detail})")
    passed_count = sum(bool(r.get('pass')) for r in results)
    passed = code == 0 and report.get('complete') and passed_count == len(results)
    return passed, f'simulation: {passed_count}/{len(results)} scenarios pass' + ('' if report.get('complete') else ', run incomplete')


def run_simulate(step):
    if station_route() == 'docker':
        return run_in_docker(step, 'simulate', need_sim=True)
    return run_ros_step(step, 'simulate', ['ros2', 'run', 'agentic_workshop', 'capstone_check'], 240,
                        'capstone-report.json', summarize_capstone, prepare=start_capstone)


def doctor_handoff(step):
    doc = Doctor('05 handoff · doctor')
    for name in ('01-reproduce', '02-repair', '03-replay', '04-simulate'):
        result = latest(name)
        if result:
            doc.ok(f'{name}: {result["outcome"]} on {result["host"]} ({result["summary"]})')
        else:
            doc.info(f'{name}: no result on this machine (fine if it ran on the station or was skipped)')
    return doc


def run_handoff(step):
    doctor_handoff(step)
    print(paint('\n== 05 handoff · run', '1'))
    head = git('rev-parse', '--short', 'HEAD')[1] if repo_state() == 'ready' else 'no commits'
    diffstat = git('diff', '--stat', BASELINE_TAG)[1] if git('rev-parse', '-q', '--verify', BASELINE_TAG)[0] == 0 else ''
    lines = ['# Run report', '', f'Drafted by lab/05-handoff.sh on {datetime.datetime.now():%Y-%m-%d %H:%M}. '
             'Fill in every [bracketed] line before you hand it off.', '',
             f'- Task and workspace revision: fix the forward-sector clearance reducer; commit {head}, '
             f'baseline {BASELINE_TAG}',
             f'- Environment: {platform.platform()}, Python {sys.version.split()[0]}',
             '- Changes made:', '', '```', diffstat or '(no diff against the baseline on this machine)', '```', '',
             '- Steps, exact commands and observed results:']
    levels = []
    for name in ('01-reproduce', '02-repair', '03-replay', '04-simulate'):
        result = latest(name)
        if not result:
            lines.append(f'  - {name}: not run on this machine [ran on a station? paste its result, or say why skipped]')
            continue
        lines.append(f'  - {name}: {result["outcome"]}, {result["summary"]}; `{"; ".join(result["commands"])}`; '
                     f'evidence: {", ".join(result["artifacts"]) or "none"}')
        if result['outcome'] == 'pass' and result['evidence']:
            levels.append(result['evidence'])
    lines += ['', '- What this establishes: ' + ('; '.join(dict.fromkeys(levels)) or '[nothing passed yet]') +
              '. No physical sensor or robot was used.',
              '- One check I did not run: [name it]',
              '- Next bounded task: [one input, one observable result]',
              '- Did spending more tokens help my understanding? [one sentence]']
    out = RUNS / '05-handoff' / f'run-report-{stamp()}.md'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))
    print(paint(f'\nSaved {out.relative_to(ROOT)}. Edit the [bracketed] lines, then share it.', '32'))
    save_result('05-handoff', 'pass', 'run report drafted', ['bash lab/05-handoff.sh'], '', [out.relative_to(ROOT)])
    return 0


STEPS = {
    '00': ('check', 'Check this machine before the lab (about 1 minute).', None, doctor_check),
    '01': ('reproduce', 'Make a baseline commit and watch the starter fail (T+05).', run_reproduce, doctor_reproduce),
    '02': ('repair', 'Rerun the checks and show your diff after each agent edit (T+10).', run_repair, doctor_repair),
    '03': ('replay', 'ROS 2 (Docker or a station): replay the synthetic point-cloud bag (T+30).', run_replay, doctor_replay),
    '04': ('simulate', 'ROS 2 (Docker or a station): run the bounded TurtleBot3 simulation (T+38).', run_simulate, doctor_simulate),
    '05': ('handoff', 'Draft your run report from the saved results (T+48).', run_handoff, doctor_handoff),
}
SCRIPTS = {step: f'{step}-{name}.sh' for step, (name, *_) in STEPS.items()}


def main(argv):
    if not argv or argv[0] not in STEPS:
        print(__doc__)
        for step, (name, purpose, *_) in STEPS.items():
            print(f'  bash lab/{SCRIPTS[step]:<16} {purpose}')
        return 2
    step, action = argv[0], (argv[1] if len(argv) > 1 else 'run')
    name, purpose, run, doctor = STEPS[step]
    if action == 'help':
        station = ' Use  clean  to stop leftover processes.' if step in ('03', '04') else ''
        print(f'Step {step} {name}: {purpose}\nUsage: bash lab/{SCRIPTS[step]} [run|doctor|help'
              f'{"|clean" if station else ""}]  (default: run).{station}\n'
              'Each run first runs its doctor, prints every command it executes and saves results in runs/.')
        return 0
    if action == 'clean' and step in ('03', '04'):
        return clean(step)
    if action == 'doctor' or step == '00':
        result = doctor(step)
        failed = result if isinstance(result, int) else result.failed
        if not isinstance(result, int):
            print('\n' + ('Fix the FAIL lines above, then run the doctor again.' if failed else 'All required checks pass.'))
        return int(failed)
    if action != 'run':
        print(f'Unknown action {action!r}. Try: bash lab/{SCRIPTS[step]} help')
        return 2
    try:
        return run(step)
    except KeyboardInterrupt:
        print('\nStopped. Run the step again when ready, or its doctor if something looked wrong.')
        return 130


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
