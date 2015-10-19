from pyimagesearch.transform import four_point_transform
from pyimagesearch import imutils
from skimage.filter import threshold_adaptive
import cv2
import pytesseract
from PIL import Image
import re
import os


def formatproductarr(prodarr):
    retarr = []
    for prod in prodarr:
        prodword = prod.split()
        for index in xrange(len(prodword)):
            if isprice(prodword[index]):
                retarr.append(" ".join(prodword[:index]))
                retarr.append(strpricetofloat(prodword[index]))
    return retarr


def strpricetofloat(strprice):
    pricestr = ""
    dot = "."
    for p in re.findall(r'\d+', strprice):
        pricestr += p
        pricestr += dot
        dot = ""
    return float(pricestr)


def findmaxtotal(stringarr):
    total = 0
    for str in stringarr:
        for word in str.split():
            if isprice(word):
                pricefloat = strpricetofloat(word)
                if pricefloat > total:
                    total = pricefloat

    return total

def prodsearationindex(stringarr):
    possibletotal = ["sub", "tot"]
    for index in xrange(0, len(stringarr)):
        for pt in possibletotal:
            if stringarr[index].lower().find(pt) > -1:
                return index
    return -1


def findstorename(stringarr):
    storename = ["walmart", "sobeys", "book store"]
    for line in stringarr:
        for sn in storename:
            if line.lower().find(sn) > -1:
                return sn.title()
    return ""

def containsnumber(string):
    return any(char.isdigit() for char in string)


def sepindex(word):
    separator = ['.', ',']
    for sep in separator:
        if word.find(sep) > -1:
            return word.find(sep)
    return -1

def isprice(word):
    if not containsnumber(word):
        return False
    if word.startswith("$"):
        return True
    separatorindex = sepindex(word)
    if separatorindex == -1:
        return False
    if word[separatorindex + 1].isdigit() and word[separatorindex + 2].isdigit():
        return True
    return False


def findprice(resultarr):
    retlist = []
    for line in resultarr:
        wordarr = line.split()
        for index in xrange(len(wordarr)/2, len(wordarr)):
            if isprice(wordarr[index]):
                retlist.append(line)
    return retlist


filenamearr = ["Sobeys.jpg", "UWBOOK.jpg", "Walmart.jpeg"]

for filename in filenamearr:

    image = cv2.imread("/Users/Jack/Desktop/TestData/" + filename)
    ratio = image.shape[0] / 500.0
    orig = image.copy()
    o_height = image.shape[0]
    image = imutils.resize(image, height = 500)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)

    im2, cnts, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse = True)[:5]

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            screenCnt = approx
            break

    warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
    warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    warped = threshold_adaptive(warped, 250, offset=20)
    warped = warped.astype("uint8") * 255

    mImgFile = "/Users/Jack/Desktop/TestData/Sobyes.jpg"
    cv2.imwrite(mImgFile, imutils.resize(warped, height=o_height))

    receiptResults = pytesseract.image_to_string(Image.open(mImgFile), lang='eng').splitlines()
    retlist = findprice(receiptResults)


    storenamestr = findstorename(receiptResults)
    prodindex = prodsearationindex(retlist)
    prodarr = retlist[:prodindex]
    totalarr = retlist[prodindex+1:]

    print("Store: " + storenamestr)
    print("\nProduct:")
    prodlist = formatproductarr(prodarr)
    for index in xrange(0, len(prodlist), 2):
        print prodlist[index],
        print ("\t\t$%.2f" % prodlist[index + 1])
    print("\nTotal: $" +str(findmaxtotal(totalarr)))

    raw_input('')
    for x in xrange(30):
        print ""

