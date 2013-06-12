flashcachegroup (fcg)
===============

making fb's flashcache to cache a group of disks with a single SSD


Fcg allows admins to dynamically create groups of hard disks, and 
apply caching on the group instead of each individual disk.

Hard disks can be dynamically added to or removed from the group, 
but there always be exactly one SSD device (or partition) 
for a group.

If there are multiple SSDs on the machine, admins have the option to
combine them by LVM or RAID and then use them as a whole as the caching 
device, or they can create a seperate group on each SSD.



