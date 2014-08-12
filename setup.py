from setuptools import setup, find_packages

NAME = "flashcachegroup"
DESCRIPTION = "create cache for a group of disks"
AUTHOR = "Ziyang Li"
AUTHOR_EMAIL = "anzigly@gmail.com"
URL = "https://github.com/lihuiba/flashcachegroup"
setup(
    name=NAME,
    version="0.6.6",
    description=DESCRIPTION,
    long_description=open("README.md").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    url=URL,
    packages=find_packages(),
    scripts=["bin/fcg", "bin/fcg-easy"],
    keywords='flashcache group'
)
