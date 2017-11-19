from setuptools import setup

MAJOR = 0
MINOR = 1
RELEASE = 1

setup(
    name="Thalassa",
    version="%s.%s.%s" % (MAJOR, MINOR, RELEASE),
    description="TBD",
    url="https://github.com/Arrekin/Thalassa",
    author="Daniel Misior",
    packages=["thalassa"],
    install_requires=[
        "Twisted"
    ],
)
