from setuptools import setup

setup(
    name='biman-tl',
    version='1.0.0',
    py_modules=['biman-tl'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        biman-tl=biman-tl:cli
    ''',
)
