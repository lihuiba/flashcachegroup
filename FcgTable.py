import FcgUtils

class FcgTable:
    def __init__(self, name):
        self.name = name
        self.lines = []
        self.existed = False
        self._init_load_lines()

    def get_lines(self):
        '''get table lines'''
        return self.lines

    def set_lines(self, tableStr):
        '''set table lines from a table string'''
        tempLines = self._get_table_lines(tableStr)
        if len(tempLines) != 0:
            self.lines = tempLines

    def create(self, tableStr=''):
        '''create a table via dmsetup'''
        if self.existed:
            print 'Table %s already exist!' % self.name
            return False
        else:
            tableContent = ''
            if tableStr != '':
                tempLines = self._load_lines(tableStr)
                if len(tempLines) != 0:
                    self.lines = tempLines
                    tableContent = tableStr
            else:
                if self.is_empty():
                    print 'table lines of %s are still empty' % self.name
                    return False
                else:
                    tableContent = self._get_table_content()

            if tableContent == '':
                print 'table lines of %s are still empty' % self.name
            else:
                tmpTableFile = FcgUtils.write2tempfile(tableContent)
                cmd = 'dmsetup create %s %s' % (self.name, tmpTableFile)
                if FcgUtils.os_execue(cmd):
                    self.existed = True
                    return True
                else:
                    return False

    def delete(self):
        pass

    def reload(self):
        cmd = 'dmsetup suspend %s'%self.name
        FcgUtils.os_execue(cmd)
        tableContent = self._get_table_content()
        tmpTableFile = FcgUtils.write2tempfile(tableContent)
        cmd = 'dmsetup reload %s %s' % (self.name, tmpTableFile)
        FcgUtils.os_execue(cmd)
        cmd = 'dmsetup resume %s'%self.name
        FcgUtils.os_execue(cmd)

    def is_existed(self):
        return self.existed

    def is_empty(self):
        if self.lines == []:
            return True
        else:
            return False

    def _init_load_lines(self):
        '''load lines during init'''
        tableContent = self._get_table_str()
        if tableContent == '' or tableContent == None:
            self.lines = []
            self.existed = False
        else:
            self.lines = self._get_table_lines(tableContent)
            self.existed = True

    def _get_table_str(self):
        cmd = 'dmsetup table %s' % self.name
        tableContent = FcgUtils.os_execue(cmd)
        return tableContent

    def _get_table_lines(self, tableStr):
        if tableStr == '' or tableStr == None:
            return []
        tableStruct = []
        tableList = tableStr.split('\n')
        for tableLine in tableList:
            tableLineList = tableLine.split()
            tempDict = {}
            if len(tableLineList) == 5:
                startSec, offset, type, oriDev, oriStartSec = tableLineList
                try:
                    major, minor = [int(x) for x in oriDev.split(':')]
                    oriDev = FcgUtils.get_devname_from_major_minor(oriDev)
                except:
                    pass
                startSec, offset, oriStartSec = map(int, [startSec, offset, oriStartSec])
                tempDict = {'startSec':startSec, 'offset':offset, 'type':type, 'oriDev':oriDev, 'oriStartSec':oriStartSec}
            elif len(tableLineList) == 3:
                startSec, offset, type = tableLineList
                startSec, offset = map(int, [startSec, offset])
                tempDict = {'startSec':startSec, 'offset':offset, 'type':type}
            elif len(tableLineList) == 0:
                pass
            else:
                print 'Could NOT support table format %s' % tableLine

            if len(tempDict) != 0:
                tableStruct.append(tempDict)
        return tableStruct

    def _get_table_content(self):
        tableStruct = self.lines
        tableStr = ''
        for line in tableStruct:
            if len(line) == 5:
                tableStr += ' '.join([str(line['startSec']), str(line['offset']), line['type'], line['oriDev'], str(line['oriStartSec'])]) + '\n'
            elif len(line) == 3:
                tableStr += ' '.join([str(line['startSec']), str(line['offset']), line['type']]) + '\n'
        return tableStr
