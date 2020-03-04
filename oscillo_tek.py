import sys
import os
from datetime import datetime
import visa

args = sys.argv

rm = visa.ResourceManager()

for osc in rm.list_resources():
    if '0x0699' in osc:
        visa_addr = osc

try:
    myFieldFox = rm.open_resource(visa_addr)
except Exception as e:
    print('Failed to open the Instrument. Aborted.')
    print('*' + str(e))
    sys.exit(1)

#Set Timeout - 5 seconds
myFieldFox.timeout = 5000

# Clear the event status registers and empty the error queue
myFieldFox.write("*CLS")

# Query identification string *IDN?
myFieldFox.write("*IDN?")
print("*IDN? -> " + myFieldFox.read())

# Save image to instrument's local disk
myFieldFox.write('SAVE:IMAGe \"Temp.png\"')

# Filename from argument if exists otherwise datetime
if len(args) > 1:
    fileName = args[1]
    if not fileName.endswith ('.png'):
        fileName += '.png'
else:
    # Generate a filename based on the current Date & Time
    dt = datetime.now()
    fileName = dt.strftime("MSO4034_%Y%m%d_%H%M%S.png")

# Wait for instrument to finish writing image to disk
myFieldFox.query('*OPC?')

# Read image file from instrument
myFieldFox.write('FILESystem:READFile \"Temp.png\"')
imgData = myFieldFox.read_raw(1024*1024)

# Check file overwrite
while os.path.exists(fileName):
    ans = input('File "' + fileName + '" already exists. Do you overwrite? [y/n] ')
    if ans.lower() in ['yes', 'ye', 'y']:
        print()
        break
    elif ans.lower() in ['no', 'n']:
        print('Aborted.')
        sys.exit(1)
            
# Save image data to local disk
file = open(fileName, 'wb')
file.write(imgData)
file.close()

# Image data has been transferred to PC and saved. Delete image file from instrument's hard disk.
myFieldFox.write('FILESystem:DELEte \"Temp.png\"')
print('Saved: ' + fileName)

myFieldFox.close()
rm.close()

