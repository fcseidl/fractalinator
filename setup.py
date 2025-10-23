from setuptools import setup

setup(name='fractalinator',
      version='1.0.1',
      description='Live-drawing tool for multibrot fractals',
      url='https://github.com/fcseidl/fractalinator/',
      author='Frank Seidl',
      author_email='frankcseidl@gmail.com',
      license='MIT',
      packages=['fractalinator'],
      install_requires=[
            'numpy',
            'matplotlib',
            'convolved-noise'
      ],
      zip_safe=False)