import setuptools


setuptools.setup(
    name='homefiles',
    version='2.0',
    description='Your files, anywhere.',
    url='https://github.com/rconradharris/homefiles2',
    license='MIT',
    author='Rick Harris',
    author_email='rconradharris@gmail.com',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6'
    ],
    install_requires=[],
    entry_points={
        'console_scripts': ['homefiles = homefiles:main']
    }
)
