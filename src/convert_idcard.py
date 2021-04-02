import PIL.Image as Image
import os
import shutil
import time
import xlrd
import math


# 1268370590336878595-孙剑文-310107198103161325-1.jpg

def _CalcAllIdCardFiles(szSrcDir):
    fromAbsPath = os.path.abspath(szSrcDir)
    if not os.path.isdir(fromAbsPath):
        raise ValueError(f'找不到目录：{fromAbsPath}')

    listIdCardFiles = []
    dictK1 = {}
    dictK2 = {}

    for fname in os.listdir(szSrcDir):
        if fname.endswith("-1.jpg"):
            dictK1[fname[:-6]] = fname
        elif fname.endswith("-2.jpg"):
            dictK2[fname[:-6]] = fname

    for k, v in dictK1.items():
        if k in dictK2:
            listIdCardFiles.append(k)
    return listIdCardFiles


def ConvertIDCards(szSrcDir, szTargetDir, dictWhiteList):
    fromAbsPath = os.path.abspath(szSrcDir)
    toAbsPath = os.path.abspath(szTargetDir)
    if not os.path.isdir(fromAbsPath):
        raise ValueError(f'找不到目录文件夹：{fromAbsPath}')
    if toAbsPath == fromAbsPath:
        raise ValueError('目标文件夹和源文件夹不能相同：{toAbsPath}')
    if not os.path.isdir(toAbsPath):
        os.makedirs(toAbsPath)
        print(f"创建目标文件夹{toAbsPath}")

    listAll = _CalcAllIdCardFiles(szSrcDir)
    nSucc = 0
    nFail = 0
    for szItem in listAll:
        try:
            orderid, name, idcard = szItem.split('-')

            if dictWhiteList and orderid not in dictWhiteList:
                continue

            srcImage1 = os.path.join(fromAbsPath, f"{szItem}-1.jpg")
            srcImage2 = os.path.join(fromAbsPath, f"{szItem}-2.jpg")
            targetImage = os.path.join(toAbsPath, f"{idcard}.jpg")
            _ConvertOneIdCard(srcImage1, srcImage2, targetImage)
            nSucc += 1
            print(f"转换成功{szItem}")
        except Exception as e:
            print(f"转换失败{szItem}")
            nFail += 1
            print(e)
            import traceback
            traceback.print_stack()
    print(f"总共转换 成功:{nSucc},失败{nFail}")


def _ConvertOneIdCard(szImage1Path, szImage2Path, szTargetPath):
    from_image1 = Image.open(szImage1Path)
    from_image2 = Image.open(szImage2Path)
    w = max(from_image1.size[0], from_image2.size[0])
    h = max(from_image1.size[1], from_image2.size[1])
    to_image = Image.new('RGB', (w, h * 2))

    to_image.paste(from_image1, (0, 0))
    to_image.paste(from_image2, (0, h))
    to_image.save(szTargetPath)


def GetConfig():
    curDir = os.path.dirname(os.path.abspath(__file__))
    configFile = os.path.join(curDir, "config.json")
    xlsFile = os.path.join(curDir, "订单白名单.xlsx")

    import json
    try:
        with open(configFile, "r", encoding="utf-8") as FileObj:
            configJson = json.load(FileObj)
            return os.path.abspath(configJson["需要合并的身份证图片放在哪里"]), os.path.abspath(configJson["合并的身份证图片放在哪里"]), os.path.abspath(configJson['订单白名单'])
    except Exception as ErrObj:
        print("load config", str(ErrObj))

    return "E:/idcard", "E:/idcard/out", xlsFile


def ReadExcelFileData(szReadPath):
    # 打开excel文件
    WorkBookObj = xlrd.open_workbook(szReadPath)
    szSheetNames = WorkBookObj.sheet_names()
    WorkSheetObj = WorkBookObj.sheet_by_name(szSheetNames[0])
    print(szReadPath)

    def _CheckIsInt(xCheckValue):
        if isinstance(xCheckValue, float):
            fLessZero, fBigZero = math.modf(xCheckValue)
            if fLessZero == 0:
                xCheckValue = int(xCheckValue)
        return xCheckValue

    def _GetSaveKey(szKey):
        if isinstance(szKey, str) and szKey.endswith("]"):
            nLefeSignIndex = szKey.find("[")
            if nLefeSignIndex != -1:
                return szKey[:nLefeSignIndex]
        return szKey

    def _IsEmptyValue(xValue):
        if (xValue is None) or (isinstance(xValue, str) and len(xValue) == 0) or xValue == "":
            return True
        return False

    dictFileData = {}

    # 读取文件第一行
    listColumnNames = []
    for nColIndex in range(WorkSheetObj.ncols):
        xCellValue = WorkSheetObj.cell_value(0, nColIndex)
        if _IsEmptyValue(xCellValue):
            listColumnNames.append(None)
            continue
        listColumnNames.append(xCellValue)

    # 标记为key的顺序
    listKeyIndex = [_GetSaveKey(szKey) for szKey in listColumnNames if szKey]

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

        dictProcessData = {}
        for xCellKey, xCellValue in dictRowData.items():
            # 转换tuple_num, list_num等通用后处理
            if isinstance(xCellKey, str) and xCellKey.endswith("]"):
                for szFormatType in g_dictFormatKeyScript:
                    if xCellKey.endswith(szFormatType):
                        xCellValue = g_dictFormatKeyScript[szFormatType](xCellValue)
                        xCellKey = xCellKey.replace(szFormatType, "")
                        break

                for szFormatType in g_dictFormatMultiKeyScript:
                    if xCellKey.endswith(szFormatType):
                        xCellValue = g_dictFormatMultiKeyScript[szFormatType](xCellValue, xCellKey, dictRowData)
                        xCellKey = xCellKey.replace(szFormatType, "")
                        break

            dictProcessData[xCellKey] = xCellValue

        dictFileData[xRowKeyID] = dictProcessData

    return dictFileData, listKeyIndex


if __name__ == '__main__':
    szindir, szoutDir, xlsFile = GetConfig()
    print(szindir, szoutDir, xlsFile)
    dictOrderWhiteList = {}
    try:
        dictOrderWhiteList, listKeyIndex = ReadExcelFileData(xlsFile)
    except Exception as e:
        print(e)

    ConvertIDCards(szindir, szoutDir, dictOrderWhiteList)
    a = input('按回车键退出...')

    # ConvertIdCard("E:/idcard/1268370590336878595-孙剑文-310107198103161325.jpg-1.jpg", "E:/idcard/1268370590336878595-孙剑文-310107198103161325.jpg-2.jpg", "E:/idcard/Test.jpg")
