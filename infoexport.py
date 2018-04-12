#!/usr/bin/env python

import sys
import xlrd
from colorama import init, Fore, Back, Style

varType = {'uint', 'int', 'string'}

def GetCPPVarType(type):
    if type == 'uint':
        return 'uint32_t'
    elif type == 'int':
        return 'int32_t'
    elif type == 'string':
        return 'std::string'
    else:
        exit(-1)
    


class ColumnDesc:
    def __init__(self):
        self.svrFlag = 0
        self.cliFlag = 0
        self.colName = ""
        self.varType = ""
        self.dataVarType = ''
        self.varName = ""

    def __str__(self):
        attr = []
        attr.append("svrFlag:%d" % (self.svrFlag))
        attr.append("cliFlag:%d" % (self.cliFlag))
        attr.append("colName:%s" % (self.colName))
        attr.append("varType:%s" % (self.varType))
        attr.append("varName:%s" % (self.varName))

        return str(attr)


class TableInfo:
    def __init__(self, ename, sname, iname, infopath, cpppath):
        if infopath[-1] != '/':
            self.infoPath = infopath + '/'
        else:
            self.infoPath = infopath
        if cpppath[-1] != '/':
            self.cppPath = cpppath + '/'
        else:
            self.cppPath = cpppath
        self.infoName = iname
        self.excelName = ename
        self.sheetName = sname
        self.columns = []
        self.data = []
    
    def loadingmsg(self):
        print(Fore.GREEN + self.excelName + ' : ' + self.sheetName + '......')
        
    def errormsg(self, msg):
        print(Fore.RED + 'Error:' + msg)
        
    def loadedmsg(self):
        print(Fore.GREEN + 'Export Success!')

    def writesvrdata(self):
        svrcsvname = self.infoPath + self.infoName + ".csv"
        f = open(svrcsvname, mode='wt', encoding='utf-8')
        for col in self.columns:
            if col.svrFlag == 0:
                continue
            f.write(col.colName + ",")
        f.write("\n")
        for line in self.data:
            for colIndex in range(len(line)):
                if colIndex >= len(self.columns):
                    break
                if self.columns[colIndex].svrFlag == 0:
                    continue
                f.write(str(line[colIndex]) + ",")
            f.write("\n")
        f.close()

    def print(self):
        for coldesc in self.columns:
            print(coldesc)

    def loadfromexcel(self):
        data = xlrd.open_workbook(self.excelName)
        try:
            table = data.sheet_by_name(self.sheetName)
        except xlrd.XLRDError as error:
            self.errormsg(error)
            data.release_resources()
            return False
        
        if table.nrows < 5:
            self.errormsg('row num is less than 5')
            return False

        for colIndex in range(table.ncols):
            cols = table.col_values(colIndex, 0, 5)
            coldesc = ColumnDesc()
            coldesc.colName = cols[0]
            coldesc.cliFlag = int(cols[1])
            coldesc.svrFlag = int(cols[2])
            coldesc.varName = cols[3]
            coldesc.dataVarType = cols[4]
            if coldesc.dataVarType not in varType:
                self.errormsg(coldesc.colName + ', ' + coldesc.dataVarType + 'type not surpport ')
                return False
            coldesc.varType = GetCPPVarType(coldesc.dataVarType)
            self.columns.append(coldesc)
        for rowIndex in range(5, table.nrows):
            rows = table.row_values(rowIndex)
            line = []
            for i in range(len(rows)):
                celltype = table.cell_type(rowIndex, i)
                if celltype == xlrd.XL_CELL_NUMBER:
                    line.append(int(rows[i]))
                else:
                    line.append(rows[i])
            self.data.append(line)
        return True
            
    def writecppsource(self):
        chhname = self.cppPath + self.infoName + '.h'
        chhredefine = '_' + self.infoName + '_H_'
        f = open(chhname, mode='wt', encoding='utf-8')
        f.write('#ifndef ' + chhredefine + '\n')
        f.write('#define _' + self.infoName + '_H_\n')
        f.write('\n\n')
        f.write('#include "base/CsvParser.h"\n')
        f.write('#include "InfoMgr.h"\n')
        f.write('\n')
        f.write('namespace info\n{\n\nstruct ' + self.infoName + '\n{\n')

        for coldesc in self.columns:
            if coldesc.svrFlag == 0:
                continue
            f.write('\t' + coldesc.varType + ' ' + coldesc.varName + ";\n")

        f.write("\n")
        f.write('\tint32_t Load(const base::CsvParser::Row & row);\n')
        f.write('\tvirtual bool Check() { return true; }\n')
        f.write('};\n')
        f.write('\n')
        f.write('typedef InfoMgr<' + self.infoName + '> ' + self.infoName + 'Mgr;\n')
        f.write('\n')
        f.write('}\n')
        f.write('\n\n')
        f.write('#endif // ' + chhredefine)

        f.close()

        cppname = self.cppPath + self.infoName + '.cpp'
        f = open(cppname, mode='wt', encoding='utf-8')

        f.write('#include "Config.h"\n')
        f.write('#include "' + self.infoName + '.h"\n')
        f.write('\n\n')

        f.write('namespace info\n{\n')
        f.write('\n')

        f.write('int32_t ' + self.infoName + '::Load(const base::CsvParser::Row& row)\n{\n')

        realIndex = 0
        for coldesc in self.columns:
            if coldesc.svrFlag == 0:
                continue
            f.write('\tthis->' + coldesc.varName + ' = row.As<' + coldesc.varType + '>(' + str(realIndex) + ');\n')
            realIndex = realIndex + 1

        f.write('\n')
        f.write('\treturn 0;\n')
        f.write('}\n')

        f.write('\n')

        f.write('}\n')

        f.close()


if __name__ == '__main__':
    init(autoreset=True)
    if len(sys.argv) < 6:
        print(Fore.GREEN + "infoexport excel_namae sheet_name info_name infopath c++sourcepath")
        exit(-1)
    
    ti = TableInfo(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    ti.loadingmsg()
    if not ti.loadfromexcel():
        exit(-1)
    ti.writesvrdata()
    ti.writecppsource()
    ti.loadedmsg()
    #ti.print()
    #print(ti.data)





