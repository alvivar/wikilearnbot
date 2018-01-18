"""
    Create an .exe with cx_Freeze, by calling 'python setup.py build'.
"""

from cx_Freeze import Executable, setup

OPTIONS = {
    'build_exe': {
        'includes': ['Queue.multiprocessing', 'idna.idnadata']
    }
}

EXECUTABLES = [Executable('wikilearnbot.py', targetName='wikilearnbot.exe')]

setup(
    name='wikilearnbot',
    version='0.1',
    description="Bot that tweets random articles with images from Wikipedia",
    executables=EXECUTABLES,
    options=OPTIONS)
