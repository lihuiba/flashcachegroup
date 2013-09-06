flashcachegroup (fcg)
================================

making fb's flashcache to cache a group of disks with one or multiple SSDs.

Fcg allows admins to dynamically create groups of hard disks, and 
apply caching on the group instead of each individual disk.


Requirements
============

Python
------
Python 2.6 and 2.7 (does **NOT** support Python 3.x)

Modules
-------
* flashcache

Install (Linux)
===========================

The easiest way to install is with pip::

    sudo pip install flashcachegroup

Or manually (assuming all required modules are installed on your system)::

    sudo python ./setup.py install

Usage
=====================

to create a new group by using hard disks:

    fcg create [-h] [-g GROUP] [-d DISK [DISK ...]] [-c CACHEDEV [CACHEDEV ...]]

to delete an *UNUSED* group:

    fcg delete [-h] [-g GROUP]

to replace broken SSDs:

	fcg rep-ssd [-h] [-g GROUP] [-c CACHEDEV [CACHEDEV ...]]