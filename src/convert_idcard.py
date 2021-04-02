import PIL.Image as Image
import os
import shutil
import time


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


def ConvertIDCards(szSrcDir, szTargetDir):
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
    import json
    try:
        with open(configFile, "r") as FileObj:
            configJson = json.load(FileObj)
            return configJson["input_dir"], configJson["output_dir"]
    except Exception as ErrObj:
        print("load config", str(ErrObj))

    return "E:/idcard", "E:/idcard/out"


if __name__ == '__main__':
    szindir, szoutDir = GetConfig()
    ConvertIDCards(szindir, szoutDir)
    a = input('按回车键退出...')

    # ConvertIdCard("E:/idcard/1268370590336878595-孙剑文-310107198103161325.jpg-1.jpg", "E:/idcard/1268370590336878595-孙剑文-310107198103161325.jpg-2.jpg", "E:/idcard/Test.jpg")
