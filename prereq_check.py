# make sure you have installed microsoft access database engine redistrinbutable
# https://www.microsoft.com/en-us/download/details.aspx?id=13255

# also need to pip install pypyodbc

# Need 32 bit version of Python, 32 bit version of Access, and 32 bit version
# of drivers.

# Check this with the following:
# python --version
# open Word -> File menu -> Account ->  Click "About Word" -> read the top line

import pypyodbc
from pprint import pprint

drivers = [x for x in pypyodbc.drivers()]
print("Below are your drivers:")
pprint(drivers)
print("You should see Microsoft Access Driver (*.mdb, *.accdb) in here.")

access_driver = ["Microsoft Access Driver (*.mdb, *.accdb)" in x for x in drivers]
try:
    assert(any(access_driver))
    print()
    print("Good to go!")
    print()
except AssertionError:
    print("You are missing the required Access driver!!  :'(")

