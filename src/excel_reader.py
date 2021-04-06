import xlrd
import math


def _CheckIsInt(xCheckValue):
    if isinstance(xCheckValue, float):
        fLessZero, fBigZero = math.modf(xCheckValue)
        if fLessZero == 0:
            xCheckValue = int(xCheckValue)
    return xCheckValue


def _IsEmptyValue(xValue):
    if (xValue is None) or (isinstance(xValue, str) and len(xValue) == 0) or xValue == "":
        return True
    return False


def ReadExcelFileData(szReadPath):
    # 打开excel文件
    WorkBookObj = xlrd.open_workbook(szReadPath)
    szSheetNames = WorkBookObj.sheet_names()
    WorkSheetObj = WorkBookObj.sheet_by_name(szSheetNames[0])

    dictFileData = {}

    # 读取文件第一行
    listColumnNames = []
    for nColIndex in range(WorkSheetObj.ncols):
        xCellValue = WorkSheetObj.cell_value(0, nColIndex)
        if _IsEmptyValue(xCellValue):
            listColumnNames.append(None)
            continue
        listColumnNames.append(xCellValue)

    # 标记为key的顺序0
    listKeyIndex = [szKey for szKey in listColumnNames if szKey]
    # 从第2行开始读取
    for nRowsIndex in range(1, WorkSheetObj.nrows):
        xRowKeyID = WorkSheetObj.cell_value(nRowsIndex, 0)
        xRowKeyID = _CheckIsInt(xRowKeyID)
        if _IsEmptyValue(xRowKeyID):
            continue

        if xRowKeyID in dictFileData:
            print("重复ID: {}, 表{}".format(xRowKeyID, szReadPath))
            continue

        dictRowData = {}
        for nColIndex in range(WorkSheetObj.ncols):
            xCellValue = WorkSheetObj.cell_value(nRowsIndex, nColIndex)
            xCellValue = _CheckIsInt(xCellValue)
            if _IsEmptyValue(xCellValue):
                continue

            xCellKey = listColumnNames[nColIndex]
            if xCellKey is None:
                continue
            dictRowData[xCellKey] = xCellValue
        dictFileData[xRowKeyID] = dictRowData

    return dictFileData, listKeyIndex
