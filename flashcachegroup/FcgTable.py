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

    def _adjust_lines(self):
        '''Merge adjacent error line in table struct '''
        tableStruct = self.lines
        adjustTable = []
        preSec = 0
        preOffset = 0
        preType = ''
        for line in tableStruct:
            if len(line) == 3:
                startSec, offset, type = [line['startSec'], line['offset'], line['type']]
                assert line['type'] == 'error', 'something WRONG in group table'
                if preType == 'error':
                    preOffset += offset
                else:
                    preSec, preOffset, preType = [startSec, offset, type]
            elif len(line) == 5:
                startSec, offset, type, oriDev, oriStartSec = [line['startSec'], line['offset'], line['type'], line['oriDev'], line['oriStartSec']]
                if preType == 'error':
                    tempDict = {'startSec':preSec, 'offset':preOffset, 'type':preType}
                    adjustTable.append(tempDict)
                adjustTable.append(line)
                preSec, preOffset, preType = [startSec, offset, type]
        if preType == 'error':
            tempDict = {'startSec':preSec, 'offset':preOffset, 'type':preType}
            adjustTable.append(tempDict)
        self.lines = adjustTable

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
                try:
                    FcgUtils.os_execute(cmd)
                    self.existed = True
                    return True
                except Exception, ErrMsg:
                    print cmd + ': ',
                    print ErrMsg
                    self.delete()
                    return False

    def delete(self):
        if self.is_existed():
            cmd = 'dmsetup remove %s'%self.name
            try:
                FcgUtils.os_execute(cmd)
                self.existed = False
                return True
            except Exception, ErrMsg:
                print cmd + ': ',
                print ErrMsg
                return False
        else:
            print 'Table %s does NOT existed...' % self.name
            return False

    def reload(self):
        self._adjust_lines()
        cmd = 'dmsetup suspend %s'%self.name
        try:
            FcgUtils.os_execute(cmd)
        except Exception, ErrMsg:
            print cmd + ': ',
            print ErrMsg
        tableContent = self._get_table_content()
        tmpTableFile = FcgUtils.write2tempfile(tableContent)
        cmd = 'dmsetup reload %s %s' % (self.name, tmpTableFile)
        try:
            FcgUtils.os_execute(cmd)
        except Exception, ErrMsg:
            print cmd + ': ',
            print ErrMsg
        cmd = 'dmsetup resume %s'%self.name
        try:
            FcgUtils.os_execute(cmd)
        except:
            print cmd + ': ',
            print ErrMsg

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
            try:
                self.lines = self._get_table_lines(tableContent)
            except:
                self.lines = []
            self.existed = True

    def _get_table_str(self):
        cmd = 'dmsetup table %s' % self.name
        try:
            tableContent = FcgUtils.os_execute(cmd)
            return tableContent
        except:
            return None

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
                #print 'Could NOT support table format %s' % tableLine
                pass

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
