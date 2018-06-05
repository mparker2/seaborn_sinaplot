from setuptools import setup


setup(
    name='sinaplot',
    version='0.1',
    description=(
        'Draws Sinaplots with matplotlib and seaborn'
    ),
    author='Matthew Parker',
    packages=[
        'sinaplot',
    ],
    install_requires=[
        'numpy',
        'matplotlib',
        'seaborn',
    ],
)