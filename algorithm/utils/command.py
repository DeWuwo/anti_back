import subprocess
from subprocess import CalledProcessError, TimeoutExpired


class Command:
    @classmethod
    def command_run(cls, command: str, time_limit=5*3600):
        try:
            ret = subprocess.run(command, shell=True, check=True, encoding="utf-8", timeout=time_limit)
            return ret.returncode == 0
        except CalledProcessError:
            print(f'command run error --- {command}')
        except TimeoutExpired:
            print(f'command run timeout --- {command}')
