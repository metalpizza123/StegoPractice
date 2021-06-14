import cv2
import sys
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from cryptography.fernet import Fernet

#######################
#Selects host image
def selectHost():
    #Ask for image name
    # hostImageLoc=input("Please enter the location of your host image")
    hostImageName = filedialog.askopenfilename(initialdir = "./", title = "Select stego image",
                                               filetypes = [('PNG',"*.png")])
    # print(hostImageName)
    hostImage = cv2.imread(hostImageName)
    # print(hostImage)
    if (hostImage is None):
        noImageAnswer=messagebox.askyesno("No Image Chosen",
                                          "No Image Chosen, would you like retry")
        if (noImageAnswer == True):
            hostImage=selectHost()
        else:
            sys.exit()
    else:
        cv2.imshow(hostImageName, hostImage)
        confirmImage=messagebox.askyesno("Image Confirm",
                                          "Is this the image you want to decode")
        if (confirmImage == True):
            # cv2.waitKey(0)
            cv2.destroyAllWindows()
            return hostImage
        else:
            hostImage=selectHost()
            return hostImage

def decimalByteToBinaryList(x):
    #returns a list of chars, a binary represenatation of input decimal byte value
    intBINlist=[0]*7
    BINstring=((str(bin(x)[2:])))
    for x in range(1, len(BINstring)+1):
        if BINstring[-x] is not None:
            intBINlist[-x]=int(BINstring[-x])
    #NOTE-returns a list of binary int, 7 items.
    return intBINlist

def extractText(inputImage):
    imageH, imageW = inputImage.shape[:2]
    #Essentially keep extracting until we find a NULL character
    #which is 7 0 bits in a row, or 0000000.
    outputList=[]
    nullFlag=False
    charList=[]
    currentChar=[]
    counterH=0
    counterW=0
    counterRGB=0
    while nullFlag==False:
        value=int((inputImage[counterH][counterW][counterRGB])%2)
        currentChar.append(value)
        # across RGB values
        #Every 7 bits we add the most recent block to the end of
        #the list of char bits. This is also where we check if the last 7
        #bits are 0 to check for the nullFlag
        if len(currentChar) == 7:
            #If we have a complete character
            #check if null
            if currentChar==[0,0,0,0,0,0,0]:
                nullFlag=True
                break
            #else it's a legitimate char, add to sequential list
            else:
                convchar=""
                for x in currentChar:
                    convchar+=str(x)
                    currentChar=[]
                charList.append(convchar)
        #Move to next value in RGB
        if counterRGB==2:
            counterRGB=0
            if (counterW==imageW-1):
                #end of image line
                counterW=0
                if counterH==imageH-1:
                    #End of image
                    nullFlag=True
                else:
                    counterH+=1
            else:
                counterW+=1
        else:
            counterRGB+=1
    return charList

def decodeASCII(inputList):
    outputstring=""
    for x in inputList:
        outputstring+=chr(int(x,2))
    return outputstring

def saveText(inputText):
    saveName = filedialog.asksaveasfilename(title='Save file as',initialfile='output.txt', defaultextension=".txt",
                                            filetypes=[('Text File',"*.txt")])
    if saveName is None: # asksaveasfile return `None` if dialog closed with "cancel".
        noSaveFileChosen=messagebox.askyesno("No save location chosen",
                                          "No save location chosen would you like retry")
        if (noSaveFileChosen == True):
            saveText(inputText)
        else:
            sys.exit()
    else:
        file=open(saveName,'w')
        file.write(inputText)
        file.close()
######################
def askForKey():
    keyfile = filedialog.askopenfilename(initialdir = "./", title = "Select Key",
                                               filetypes = [('Text Files',"*.txt")])
    #Check whether user chose a file]
    try:
        file=open(keyfile, 'r')
        key=file.read()
        file.close()
    except:
        if (keyfile == ""):
            noChosenFile=messagebox.askyesno("No key file chosen",
                                              "No key file chosen, would you like retry")
            if (noChosenFile == True):
                text2Hide=askForKey()
            else:
                sys.exit()
        else:
            sys.exit()
    key=str.encode(key)
    return key

def decodeWithKey(ciphertext,key):
    f = Fernet(key)
    output=f.decrypt(str.encode(ciphertext))
    output=output.decode()
    return output
#START
root = tkinter.Tk()
root.withdraw()
#######################
### SELECT HOST
coverImage = selectHost()
key=askForKey()
##EXTRACT THE TEXT OUT OF IMAGE
outputImage = extractText(coverImage)
ciphertext=decodeASCII(outputImage)
outputText=decodeWithKey(ciphertext,key)
saveText(outputText)
##
root.destroy()
