from setuptools import setup, find_packages

VERSION = (0, 1, 0)

def version():
    v = ".".join(str(v) for v in VERSION)
    cnt = f'__version__ = "{v}" \n__version_full__ = __version__'
    with open('pypeak/version.py', 'w') as f:
        f.write(cnt)
    return v

setup(
    name='pypeak',
    version=version(),
    packages=find_packages(include=['pypeak*']),
)