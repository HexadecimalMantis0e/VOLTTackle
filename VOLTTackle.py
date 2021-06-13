import os
import struct
import argparse
import zlib


parser = argparse.ArgumentParser()
parser.add_argument("directory")
parser.add_argument("-n", "--nopad", action = "store_true", help = "Disable padding")
args = parser.parse_args()

nameLength = 0x00
nameOffset = 0x00
startAddress = 0x800
needPadCheck = False
paddingSize = 0x00

print("Creating VOLT archive...")
fileList = os.listdir(args.directory)
f0 = open(args.directory + ".vol", "wb")
numOfFiles = len(fileList)

for fileName in fileList:
    nameLength += len(fileName) + 0x11

f0.write("VOLT".encode())
f0.write(struct.pack('I', 0x02))
f0.write(struct.pack('I', numOfFiles))
f0.write(struct.pack('I', nameLength))

# Handle name hash section
for fileName in fileList:
    nameHash = zlib.crc32(fileName.encode())
    f0.write(struct.pack('I', nameHash))
    f0.write(struct.pack('I', 0x01))
    f0.write(struct.pack('I', nameOffset))
    nameOffset += (0x11 + len(fileName))

# Calculate main padding bytes
padLength = 0x800 - (nameLength + 0x10 + (numOfFiles * 0x0C))

# Handle fileList section
for fileName in fileList:
    f0.write(struct.pack('I', startAddress))
    f0.write(struct.pack('I', 0x00))
    filePath = os.path.join(args.directory, fileName)
    f1 = open(filePath, "rb")

    if args.nopad != True:
        header = f1.read(4).decode()

        # pad everything that isn't a strat WAD
        if header != "BIGB":
            needPadCheck = True

    f1.seek(0x00, os.SEEK_END)
    size = f1.tell()
    f1.seek(0x00, os.SEEK_SET)

    if needPadCheck == True:
        print("Padding " + fileName)
        paddingSize = 0x800 - (size % 0x800)
        startAddress += paddingSize
    else:
        print(fileName)

    f0.write(struct.pack('I', size))
    f0.write(struct.pack('I', 0x00))
    f0.write(fileName.encode())
    f0.write(struct.pack('B', 0x00))
    goBack = f0.tell()

    if needPadCheck == True:
        padAddress = startAddress - paddingSize
        f0.seek(padAddress, os.SEEK_SET)
    else:
        f0.seek(startAddress, os.SEEK_SET)

    fileBytes = f1.read(size)
    f0.write(fileBytes)

    if needPadCheck == True:
        f0.write(bytearray([0x69]) * paddingSize)
        needPadCheck = False

    f0.seek(goBack, os.SEEK_SET)
    startAddress += size
    f1.close()

# Write main padding
f0.write(bytearray([0x69]) * padLength)
print("Done!")
f0.close()
