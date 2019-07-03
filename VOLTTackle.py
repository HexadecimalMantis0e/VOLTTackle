import os
import struct
import argparse
import zlib

parser = argparse.ArgumentParser()
parser.add_argument("directory")
args = parser.parse_args()

address = 0x00
needPadCheck = False
namelength = 0x00
paddingsize = 0x00
names = []

print "Creating VOLT archive..."

filelist = os.listdir(args.directory)
f0 = open(args.directory+".vol","wb")
number_files = len(filelist)

for filename in os.listdir(args.directory):
    namelength += len(filename) + 0x11
    names += [filename]

f0.write("VOLT")
f0.write(struct.pack("i", 0x02))
f0.write(struct.pack("i", number_files))
f0.write(struct.pack("i", namelength))

# Handle name hash section
for i in range(0,number_files):
    namehash = zlib.crc32(names[i])
    f0.write(struct.pack("i", namehash))
    f0.write(struct.pack("i", 0x01))
    f0.write(struct.pack("i", address))
    address += (0x11 + len(names[i]))

# Calculate main padding bytes
padlength = 0x800 - (namelength + 0x10 + (number_files * 0x0C))

startaddr = 0x800

# Handle filelist section
for filename in os.listdir(args.directory):
    f0.write(struct.pack("i", startaddr))
    f0.write(struct.pack("i", 0x00))

    fpath = os.path.join(args.directory, filename)
    f1 = open(fpath, "rb")

    header = f1.read(4)

    # pad everything that isn't a strat
    if header != "BIGB":
        needPadCheck = True

    f1.seek(0x00, os.SEEK_END)
    size = f1.tell()
    f1.seek(0x00, os.SEEK_SET)

    if needPadCheck == True:
        print "Padding " + filename
        paddingsize = 0x800 - (size % 0x800)
        startaddr += paddingsize
    else:
        print filename

    f0.write(struct.pack("i", size))
    f0.write(struct.pack("i", 0x00))
    f0.write(filename)
    f0.write(bytearray([0]))

    GoBack = f0.tell()

    if needPadCheck == True:
        padaddr = startaddr - paddingsize
        f0.seek(padaddr, os.SEEK_SET)
    else:
        f0.seek(startaddr, os.SEEK_SET)

    filebytes = f1.read(size)
    f0.write(filebytes)

    if needPadCheck == True:
        f0.write(bytearray([0x69])*paddingsize)
        needPadCheck = False

    f0.seek(GoBack, os.SEEK_SET)
    startaddr += size
    f1.close()

# Write main padding
f0.write(bytearray([0x69])*padlength)

f0.close()
