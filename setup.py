from setuptools import setup, find_packages
NAME="flashcachegroup"
DESCRIPTION="create cache for a group of disks"
AUTHOR="Ziyang Li"
AUTHOR_EMAIL="lzynudt@gmail.com"
URL="https://github.com/lihuiba/flashcachegroup"
setup(
    name=NAME,
    version="0.2.4",
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    url=URL,
    packages=find_packages(),
    scripts = ["bin/fcg"],
    keywords='flashcache group'
)
