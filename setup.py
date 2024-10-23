from setuptools import setup

setup(name='fractalinator',
      version='1.0',
      description='Live-drawing tool for multibrot fractals',
      url='https://github.com/fcseidl/fractalinator/',
      author='Frank Seidl',
      author_email='frankcseidl@gmail.com',
      license='MIT',
      packages=['fractalinator'],
      install_requires=[
            'numpy',
            'matplotlib'
      ],
      zip_safe=False)