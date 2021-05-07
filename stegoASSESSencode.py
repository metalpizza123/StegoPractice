import sys
import tkinter
from tkinter import filedialog
from tkinter import messagebox

import cv2
import numpy

def selectHost():
    #Ask for image name
    # hostImageLoc=input("Please enter the location of your host image")
    hostImageName = filedialog.askopenfilename(initialdir = "./", title = "Select cover image",
                                               filetypes = [('PNG',"*.png")])
    # print(hostImageName)
    hostImage = cv2.imread(hostImageName,-1)
    # print(hostImage)

    if (hostImage is None):
        noImageAnswer = messagebox.askyesno("No Image Chosen",
                                          "No Image Chosen, would you like retry")
        if (noImageAnswer == True):
            hostImage=selectHost()
        else:
            sys.exit()
    else:
        cv2.imshow(hostImageName, hostImage)
        confirmImage = messagebox.askyesno('Confirm Image',
                                          "Is this image ok?")
        if (confirmImage == True):
            # cv2.waitKey(0)
            cv2.destroyAllWindows()
            return hostImage
        else:
            cv2.destroyAllWindows()
            hostImage = selectHost()
            return hostImage

def extractAlpha(inputImage):
    #In OpenCV, the 4th layer is the alpha, as it's store BGRA
    channels = cv2.split(inputImage)
    return channels[3]

def extractBGR(inputImage):
    #In OpenCV, the 4th layer is the alpha, as it's store BGRA
    channels = cv2.split(inputImage)
    rgbImage = cv2.merge((channels[0], channels[1], channels[2]))
    return rgbImage

def combineBGRAlpha(RGBImage,alphaMask):
    RGBchannels = cv2.split(RGBImage)
    outputImage = cv2.merge((RGBchannels[0], RGBchannels[1], RGBchannels[2], alphaMask))
    return outputImage

def askText():
    secretTextFile = filedialog.askopenfilename(initialdir = "./", title = "Select secret text",
                                               filetypes = [('Text Files',"*.txt")])
    #Check whether user chose a file]
    try:
        file2Hide=open(secretTextFile, 'r')
        text2Hide=file2Hide.read()
        file2Hide.close()
    except:
        if (secretTextFile == ""):
            noChosenFile=messagebox.askyesno("No Text File Chosen",
                                              "No Text File Chosen, would you like retry")
            if (noChosenFile == True):
                text2Hide=askText()
            else:
                sys.exit()
        else:
            sys.exit()

    return text2Hide

def decimalByteToBinaryList(x):
    #returns a list of chars, a binary represenatation of input decimal byte value
    intBINlist=[0]*7
    BINstring=((str(bin(x)[2:])))
    for x in range(1, len(BINstring)+1):
        if BINstring[-x] is not None:
            intBINlist[-x]=int(BINstring[-x])
    #NOTE-returns a list of binary int, 7 items.
    return intBINlist

def encodeText(inputListDecimalByte):
    bitList = []
    for x in inputListDecimalByte:
        bitList.append(decimalByteToBinaryList(ord(x)))
    return bitList

def hideText(inputImage,inputTextList):
    #It's not a list of text... necessarily. it's a list of chars coded in ASCII binary
    imageH, imageW = inputImage.shape[:2]
    outputImage=numpy.zeros((imageH,imageW,3))
    inputsize= len(inputTextList)*len(inputTextList[1])
    # slice out the last bit of each pixel in the original and replace it with either a value
    # from the list, or if out of stuff to hide, replace with 0
    # ITER through all the bits, LOOP through each pixel, then R,G,B
    # We know how many chars there will be so we can count up to it using inputsize
    counter=0
    deadflag=7
    for h in range(0,imageH):
        for w in range(0,imageW):
            for rgb in range(0,3):
                # across RGB values
                if counter<inputsize:
                    value = int((inputImage[h][w][rgb]) - (inputImage[h][w][rgb]) % 2)
                    #0 the last bit
                    charPos = counter//7
                    bitPos = counter%7
                    value += inputTextList[charPos][bitPos]
                    counter += 1

                elif (deadflag>0):
                    #this executes for 7 times, and ensures there's a "dead" sequence to end the message.
                    #It inserts the 0 bit at the end  as a flag
                    value = int((inputImage[h][w][rgb]) - (inputImage[h][w][rgb]) % 2)
                    deadflag -= 1

                else:
                    #restores original value
                    value = int((inputImage[h][w][rgb]))

                # value = int((inputImage[h][w][rgb]))
                outputImage[h][w][rgb] = value
    outputImage=outputImage.astype('uint8')
    return outputImage

def saveImage(outputImage):
    saveName = filedialog.asksaveasfilename(initialdir = "./", title='Save file as', initialfile='output.png',
                                            defaultextension=".png", filetypes=[('PNG',"*.png")])
    if saveName is None: # asksaveasfile return `None` if dialog closed with "cancel".
        noSaveFileChosen=messagebox.askyesno("No save location chosen",
                                          "No save location chosen would you like retry")
        if (noSaveFileChosen == True):
            saveImage(outputImage)
        else:
            sys.exit()
    else:
        cv2.imwrite(saveName,outputImage)

def hasAlpha(inputImage):
    if (inputImage.shape[2]==4):
        return True
    else:
        return False

def checkSize(inputImage, bitText):
    imageH, imageW = inputImage.shape[:2]
    charCapacity = (imageH * imageW * 3)
    charAmount=(len(bitText)*7)+7
    #The +7 at the end is for inserting the ending char, ASCII value 0
    if (charAmount > charCapacity):
        noChosenFile = messagebox.showerror("Message too large",
                                           "The chosen message is too large to hide in the chosen image")
        sys.exit()



######################

#START
#Spawn and hide root window
root = tkinter.Tk()
root.withdraw()
#######################

# SELECT cover image
hostImage = selectHost()
alphaValue = hasAlpha(hostImage)
##ASK FOR TEXT
targetText = askText()
bitText = encodeText(targetText)
#Check for size
checkSize(hostImage, bitText)

if (alphaValue):
    alphaMask=extractAlpha(hostImage)
    BGRimage=extractBGR(hostImage)
    ##HIDE THE TEXT IN IMAGE
    outputBGRImage = hideText(BGRimage,bitText)
    #combine the image  alpha back in
    combinedImage=combineBGRAlpha(outputBGRImage,alphaMask)
else:
    ##HIDE THE TEXT IN IMAGE
    combinedImage = hideText(hostImage,bitText)
##SAVE TO FILE
saveImage(combinedImage)

## Kill root window
root.destroy()

#####################
