flashcachegroup (fcg)
=====================

fcg makes fb's flashcache to cache a group of disks with one or multiple SSDs.

Group of hard disk(s) can be dynamically created , and caching can be applied
on the group instead of each individual disk.

Hard disk(s) can be dynamically added to or removed from the group on demand.

In case of failure(s), SSD(s) can be replaced transparently, without interrupting
upper layers.


principle
=========================
Figure 1(a) shows the structure of a cached group of HDs, and figure 1(b) adds
some explanation, which can be described as follow: 
1. Fcg respectively combines the group of HDs and all the SSDs, with dm-linear.
2. Fcg invokes flashcaceh-create to cache the group of HDS with SSDs.
3. Fcg splites the hard disks out from the cached group, with dm-linear too.
![alt tag](https://raw.github.com/lihuiba/flashcachegroup/branch/doc/fcg-structure.png)
figure 1(a)

![alt tag](https://raw.github.com/lihuiba/flashcachegroup/branch/doc/fcg-structure-explained.png)
figure 1(b)


Usage
=====================

to create a new group by using hard disks:

    fcg create [-h] [-g GROUP] [-d DISK [DISK ...]] [-c CACHEDEV [CACHEDEV ...]]

to delete an *UNUSED* group:

    fcg delete [-h] [-g GROUP]

to replace broken SSDs:

	fcg rep-ssd [-h] [-g GROUP] [-c CACHEDEV [CACHEDEV ...]]


Requirements
=====================

Python
------
Python 2.6 and 2.7 (does **NOT** support Python 3.x)

Modules
-------
* flashcache

Installation 
=====================

The easiest way to install is with pip::

    sudo pip install flashcachegroup

Or manually (assuming all required modules are installed on your system)::

    sudo python ./setup.py install

