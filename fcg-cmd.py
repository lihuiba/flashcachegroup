#!/usr/bin/env python
import sys, cmd
class FcgCmd(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = 'fcg>'

    def help_quit(self):
        print 'Quit the program'

    def __bytes2sectors(self, bytes):
        if bytes.endswith('G') or bytes.endswith('g'):
            bytes = int(bytes[:-1])*1024*1024*1024
        elif bytes.endswith('M') or bytes.endswith('m'):
            bytes = int(bytes[:-1])*1024*1024
        elif bytes.endswith('K') or bytes.endswith('k'):
            bytes = int(bytes[:-1])*1024
        else:
            bytes = int(bytes)*1024*1024
        sectors = bytes/512
        return sectors
    def __os_execue(self, cmd):
        try:
            os.system(cmd)
            return True
        except:
            print 'Execute %s failed!' % cmd
            return False

    def do_quit(self, line):
        sys.exit()
    def do_exit(self, line):
        self.do_quit(line)

    def do_create(self, cmdline):
        hddSectors = self.__bytes2sectors(hddSzie)
        dmTable = '0 %s error' % hddSectors
        cmd = 'dmsetup create %s %s' % (groupName, dmTable)
        ret = self.__os_execue(cmd)
        if ret == False:
            return

    def do_delete(self, groupName):
        pass

    def do_show(self, groupName):
        pass

    def do_add(self):
        pass

if __name__ == '__main__':
    fcg = FcgCmd()
    fcg.cmdloop()
