from setuptools import find_packages, setup

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
    name='D4_accessibility',
    package_dir={"": "src"},
    packages=find_packages('src'),
    version='0.0.0',
    description='D4 Accessibility project',
    long_description=long_description,
    author='Charles Rudder',
    license='MIT',
)
