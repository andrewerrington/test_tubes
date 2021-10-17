# Program to illustrate scanning a switch matrix attached to MCP23017
# GPIO port expander on the I2C bus.

# Andrew Errington October 2021

# Public domain code. No warranty express or implied.

import smbus    # Driver for I2C bus
import time

DEVICE = 0x20   # MCP23017 default I2C address

IODIRA = 0x00   # Port A direction register
IODIRB = 0x01   # Port B direction register
PULUPA = 0x0C   # Port A pullup register
PULUPB = 0x0D   # Port B pullup register
OLATA  = 0x14   # Port A output register
OLATB  = 0x15   # Port B output register
GPIOA  = 0x12   # Port A input register
GPIOB  = 0x13   # Port B input register

bus = smbus.SMBus(1)    # Early Pis use bus 0

# Switches are wired in a matrix, with diodes to prevent ghosting.
# Rows are on Port B, 0-3 (labelled A B C D)
# Columns are on Port A, 0-5 (labelled 1 2 3 4 5 6)
# Total array is 24 switches. Switch locations labelled A1, A2, etc.

# Switch names, indexed by (row,col)
switch_names = {
(0,0):'A1', (0,1):'A2', (0,2):'A3', (0,3):'A4', (0,4):'A5', (0,5):'A6',
(1,0):'B1', (1,1):'B2', (1,2):'B3', (1,3):'B4', (1,4):'B5', (1,5):'B6',
(2,0):'C1', (2,1):'C2', (2,2):'C3', (2,3):'C4', (2,4):'C5', (2,5):'C6',
(3,0):'D1', (3,1):'D2', (3,2):'D3', (3,3):'D4', (3,4):'D5', (3,5):'D6'
}

# Set all four rows to input with pull-ups turned on
bus.write_byte_data(DEVICE,IODIRB,0x0F) # Lower 4 bits to input
bus.write_byte_data(DEVICE,PULUPB,0x0F) # Lower 4 bits turn on pull-ups

# Set all six columns to input Hi-Z no pullup (lower 6 bits)

bus.write_byte_data(DEVICE,IODIRA,0x3F) # Lower 6 bits to input
bus.write_byte_data(DEVICE,PULUPA,0x00) # All pull-ups off
bus.write_byte_data(DEVICE,GPIOA,0x00)  # All outputs low

# Now the matrix loop. Set a column to output low, read rows. Repeat.

while True:
  switches = []     # Empty list to build up switch names
  for col in range(0,6):
    bus.write_byte_data(DEVICE,IODIRA,(0x3F ^ (1<<col))) # col bit to output
    rows = bus.read_byte_data(DEVICE,GPIOB)     # Read rows
    bus.write_byte_data(DEVICE,IODIRA,0x3F) # All cols to input again
    for row in range(0,4):
      # If any bit is 0 then the switch was pressed
      if (rows & (1<<row))==0:
        switches.append(switch_names[(row,col)])
    print(col,bin(0x3F ^ (1<<col)),bin(rows))   # Some useful debug output

  print(switches)
  print()
  time.sleep(0.2)       # Repeat five times a second
