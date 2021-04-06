import xlrd
import math
import xlwt
from xlutils.copy import copy
import os


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


def write_excel_xls(path, sheet_name, value):
    index = len(value)  # 获取需要写入数据的行数
    workbook = xlwt.Workbook()  # 新建一个工作簿
    sheet = workbook.add_sheet(sheet_name)  # 在工作簿中新建一个表格
    for i in range(0, index):
        for j in range(0, len(value[i])):
            sheet.write(i, j, value[i][j])  # 像表格中写入数据（对应的行和列）
    workbook.save(path)  # 保存工作簿


def WriteExcelAppend(path, value):
    if not os.path.isfile(path):
        b = xlwt.Workbook()
        b.add_sheet("新建")
        b.save(path)

    index = len(value)  # 获取需要写入数据的行数
    workbook = xlrd.open_workbook(path)  # 打开工作簿
    sheets = workbook.sheet_names()  # 获取工作簿中的所有表格
    worksheet = workbook.sheet_by_name(sheets[0])  # 获取工作簿中所有表格中的的第一个表格
    rows_old = worksheet.nrows  # 获取表格中已存在的数据的行数
    new_workbook = copy(workbook)  # 将xlrd对象拷贝转化为xlwt对象
    new_worksheet = new_workbook.get_sheet(0)  # 获取转化后工作簿中的第一个表格
    for i in range(0, index):
        for j in range(0, len(value[i])):
            new_worksheet.write(i + rows_old, j, value[i][j])  # 追加写入数据，注意是从i+rows_old行开始写入
    new_workbook.save(path)  # 保存工作簿
