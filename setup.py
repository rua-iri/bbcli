from setuptools import setup


setup(
    name='bbcli',
    version='0.4.0',
    description='Browse BBC News from the comand line. (Based on pyhackernews)',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    license="MIT",
    keywords='bbc news console terminal curses urwid',
    author='rua-iri',
    author_email='117874491+rua-iri@users.noreply.github.com',
    url='https://github.com/rua-iri/bbcli',
    packages=['bbcli'],
    install_requires=['urwid==2.1.1', 'requests==2.31.0', 'arrow==0.15.8'],
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Terminals',
    ],
    entry_points={
        'console_scripts': ['bbcli = bbcli.core:live']
    })
