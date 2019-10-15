from setuptools import setup

setup(
    name = 'annotate',
    author = 'Diego Morais',
    author_email = 'arthur.vinx@gmail.com',
    description = 'Annotate each query using the best alignment for which a mapping is known',
    license = 'GPL3',
    version = '1.1',
    packages = ['annotate'],
    scripts=['bin/annotate'],
    install_requires=['plyvel']
)
