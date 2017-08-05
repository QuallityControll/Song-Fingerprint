from setuptools import setup, find_packages

def do_setup():
    setup(name='song_fingerprint',
          version="1.0"
          authors='Quallitycontroll',
          description='Returns name of song that was played',
          license='MIT Beaverworks',
          platforms=['Windows', 'Linux', 'Mac OS-X', 'Unix'],
          packages=find_packages())

if __name__ == "__main__":
    do_setup()