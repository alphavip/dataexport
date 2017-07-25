#!/usr/bin/env python

import sys
import xlrd


class ColumnDesc:
    def __init__(self):
        self.svrFlag = 0
        self.cliFlag = 0
        self.colName = ""
        self.varType = ""
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

    def writesvrdata(self):
        svrcsvname = self.infoPath + self.infoName + ".csv"
        f = open(svrcsvname, "wt")
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
            print(error)
            data.release_resources()
            return

        for colIndex in range(table.ncols):
            cols = table.col_values(colIndex, 0, 5)
            coldesc = ColumnDesc()
            coldesc.cliFlag = int(cols[0])
            coldesc.svrFlag = int(cols[1])
            coldesc.colName = cols[2]
            coldesc.varName = cols[3]
            coldesc.varType = cols[4]
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
    def writecppsource(self):
        chhname = self.cppPath + self.infoName + ".h"
        chhredefine = "_" + self.infoName + "_H_"
        f = open(chhname, "wt")
        f.write("#ifndef " + chhredefine + '\n')
        f.write("#define _ItemInfo_H_\n")
        f.write('\n\n')
        f.write('#include "base/CsvParser.h"\n')
        f.write('#include "InfoMgr.h"\n')
        f.write('\n')
        f.write('namespace info\n{\n\nstruct ItemInfo\n{\n')

        for coldesc in self.columns:
            if coldesc.svrFlag == 0:
                continue
            f.write('\t' + coldesc.varType + ' ' + coldesc.varName + ";\n")

        f.write("\n")
        f.write('\tint32_t Load(const base::CsvParser::Row & row);\n')
        f.write('\tvirtual bool Check() { return true; }\n')
        f.write('};\n')
        f.write('\n')
        f.write('typedef InfoMgr<' + self.infoName + '> ' + self.infoName +'Mgr;\n')
        f.write('\n')
        f.write('}\n')
        f.write('\n\n')
        f.write('#endif // ' + chhredefine)

        f.close()

        cppname = self.cppPath + self.infoName + '.cpp'
        f = open(cppname, "wt")

        f.write('#include "Config.h"\n')
        f.write('#include "ItemInfo.h"\n')
        f.write('\n\n')

        f.write('namespace info\n{\n')
        f.write('\n')

        f.write('int32_t ItemInfo::Load(const base::CsvParser::Row& row)\n{\n')

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
    if len(sys.argv) < 6:
        print("infoexport excel_namae sheet_name info_name infopath c++sourcepath")
        exit(-1)
    ti = TableInfo(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    ti.loadfromexcel()
    ti.writesvrdata()
    ti.writecppsource()
    #ti.print()
    #print(ti.data)





