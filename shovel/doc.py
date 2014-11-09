from pathlib import Path
from shovel import task
import os
import subprocess
import webbrowser

@task
def watch():
    """Renerate documentation when it changes.

    Requires watchdog (pip install watchdog)
    """
    index = Path(os.getcwd(), 'doc', 'html', 'index.html')

    gen()
    print('\n' + str(index))
    subprocess.call(['watchmedo', 'shell-command', '--patterns=*.rst;*.py', '--ignore-pattern=_build/*', '--recursive', '--command=make -C doc/ html'])

@task
def upload():
    gen()
    subprocess.call(['python', 'setup.py', 'upload_docs', '--upload-dir=doc/_build/dirhtml'])

@task
def gen():
    subprocess.call(['make', '-C', 'doc/', 'dirhtml'])
    subprocess.call(['make', '-C', 'doc/', 'html'])
