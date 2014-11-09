from shovel import task
import subprocess

@task
def rst():
    subprocess.call(['pandoc', '--from=markdown', '--to=rst', '--output=README', 'README.md'])
