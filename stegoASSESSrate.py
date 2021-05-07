import cv2
import sys
import tkinter
from tkinter import filedialog
from tkinter import messagebox
import numpy
##

def selectHost(imageNo):
    #Ask for image name
    # hostImageLoc=input("Please enter the location of your host image")
    if imageNo==1:
        hostImageName = filedialog.askopenfilename(initialdir = "./", title = "Select COVER image",
                                               filetypes = [('PNG',"*.png")])
    elif imageNo==2:
        hostImageName = filedialog.askopenfilename(initialdir = "./", title = "Select STEGO image",
                                               filetypes = [('PNG',"*.png")])
    hostImage = cv2.imread(hostImageName)
    if (hostImage is None):
        noImageAnswer=messagebox.askyesno("No Image Chosen",
                                          "No Image Chosen, would you like retry")
        if (noImageAnswer == True):
            hostImage=selectHost(imageNo)
            return hostImage
        else:
            sys.exit()
    else:
        cv2.imshow(hostImageName, hostImage)
        confirmImage = messagebox.askyesno('Confirm Image',
                                          "Is this image ok?")
        if (confirmImage == True):
            cv2.destroyAllWindows()
            return hostImage
        else:
            cv2.destroyAllWindows()
            hostImage = selectHost(imageNo)
            return hostImage


def edgeDetect(inputImage, minVal, maxVal):
    edgeImage = cv2.Canny(inputImage,minVal,maxVal)
    return  edgeImage

def getBitPlane(inputImage,bit):
    imageH, imageW = inputImage.shape[:2]
    outputPlane = numpy.zeros((imageH, imageW, 3))
    for h in range(0, imageH):
        for w in range(0, imageW):
            for rgb in range(0, 3):
                value = (inputImage[h][w][rgb] % (2 ** (bit))) // (2 ** (bit-1))
                outputPlane[h][w][rgb] = value
    return outputPlane

def extractBGR(inputImage):
    #In OpenCV, the 4th layer is the alpha, as it's store BGRA
    channels = cv2.split(inputImage)
    rgbImage = cv2.merge((channels[0], channels[1], channels[2]))
    return rgbImage

def hasAlpha(inputImage):
    return (inputImage.shape[2]==4)

def compareBitPlane(coverImage,stegoImage,bit):
    imageH, imageW = coverImage.shape[:2]
    score=0
    hostbitplane=getBitPlane(coverImage,bit)
    coverbitplane=getBitPlane(stegoImage,bit)
    for h in range(0,imageH):
        for w in range(0,imageW):
            for rgb in range(0,3):
                value1=(hostbitplane[h][w][rgb])
                value2=(coverbitplane[h][w][rgb])
                if (value1!=value2):
                    score+=1
    return score

def compareImagePixel(coverImage, stegoImage):
    imageH, imageW = coverImage.shape[:2]
    # print(2**n)
    score = 0
    scoreList=[]
    for h in range(0, imageH):
        for w in range(0, imageW):
            for rgb in range(0, 3):
                value1 = int(coverImage[h][w][rgb])
                value2 = int(stegoImage[h][w][rgb])
                pixelColourScore=abs(value1 - value2)
                score += pixelColourScore
            scoreList.append(score)
            score=0

    #So now we have a list of bits change per pixel
    scores=[0,0,0,0,0,0,0,0]
    #score0,score1,score2,score3,score4,score5,score6,score7=0

    for x in scoreList:
        scores[x]+=1
    return scores

def checkImage(coverImage,stegoImage):
    dimension1 = coverImage.shape
    dimension2 = stegoImage.shape
    return (dimension1 == dimension2)

def scoreBit(inputScoreList):
    #I've scaled it linearly. The score is as follows:
    #For each bit a pixel varies, the error increases exponentially
    #1 bit difference is 1 point (2^0)
    #2 bit difference is 2 points (2^1)
    #3 bit difference is 4 points (2^2)
    # etc
    score = 0
    for x in range(len(inputScoreList)):
        if x==0:
            print("The number of pixels unchanged is " + str(inputScoreList[x]))
        elif inputScoreList[x]!=0:
            print("The number of pixels with " + str(x) + " bits changed is " + str(inputScoreList[x]))
            score+=((inputScoreList[x])*(2**x-1))
    return score

def scorePlane(coverImage,stegoImage):
    #I've scaled it linearly. The score is as follows:
    #For each bit a pixel varies, the error increases exponentially
    #1 bit difference is 1 point (2^0)
    #2 bit difference is 2 points (2^1)
    #3 bit difference is 4 points (2^2)
    # etc
    checkImage1bit = compareBitPlane(coverImage, stegoImage, 1)
    print("The bit plane difference for the least significant bit plane is " + str(checkImage1bit))
    checkImage2bit = compareBitPlane(coverImage, stegoImage, 2)
    print("The bit plane difference for the 2nd least significant bit plane is " + str(checkImage2bit))
    checkImage3bit = compareBitPlane(coverImage, stegoImage, 3)
    print("The bit plane difference for the 3rd least significant bit plane is " + str(checkImage3bit))
    checkImage4bit = compareBitPlane(coverImage, stegoImage, 4)
    print("The bit plane difference for the 4th least significant bit plane is " + str(checkImage4bit))
    scoreList=[checkImage1bit,checkImage2bit,checkImage3bit,checkImage4bit]
    score=0
    #In this score, the higher the value of change expnentially increases your score
    #So for every bit in a plane that changes, the more impact is has on a score. Score is then averaged, per plane
    # I'll use (1.0005^score)-1. So if a image has 1 plane with 10,000 changed pixels, the score is (147.2+0+0+0)/4=36~
    #If an image has 2 planes, with 5,000 changed pixels each, the score is (11.1+11.1+0+0)/4=5.5~
    for x in scoreList:
        if x!=0:
            score+=(1.0005**x)-1
    return score

####
root = tkinter.Tk()
root.withdraw()
##
coverImage=selectHost(1)
stegoImage=selectHost(2)
imageCheck=checkImage(coverImage,stegoImage)
if (imageCheck==False):
    noChosenFile = messagebox.showerror("Images not matching resolution",
                                        "The images chosen don't match resolution")
    sys.exit()
rawBitDifference=compareImagePixel(coverImage,stegoImage)
pixelScore=scoreBit(rawBitDifference)
print("The score for pixel bit change is  " + str(pixelScore))


bitPlaneScore=scorePlane(coverImage,stegoImage)
print("The score for bit plane change is  " + str(bitPlaneScore))

##

root.destroy()

####