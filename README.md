SMS: Spam Mailing Service (former CMS - CON Mailing Service)
============================================================
Python script that monitors PVs EPICS, check their specified operation values and send an e-mail
to a list of targets with a warning message if the PV value exceed its limits.

This code reads a list of EPICS PVs and their corresponding specified values
from a CSV file and monitor them. If any these PVs is not in it's specified
value, an e-mail is sent with a warning message to one or a list of e-mail
address.

So far, it's monitoring the following systems:

    - water temperature of Linac Klystron 1
    - water temperature of Linac Klystron 2
    - water temperature of Linac Accelerating Structures
    - total dose of radiation detectors (Thermo, ELSE, Berthold)

To do:
----------

    - if cell is empty, its breaking the code
    - from time to time read csv file to update tables (?)
    - support for condition 'decreasing step' (similar to 'increasing step')
    - loop for generating PVs according to csv colums (check "test.py")
    - supervisory for the SMS (Spam Mail Server) --> PyDM? Web?
    - load supervisory by reading csv file (similar to this code)

Syntax:
----------
    - cells should not be left empty!
    - separate e-mails with semicolon (";") and no space
        e.g.: "rafael.ito@lnls.br;ito.rafael@gmail.com"
    - separate specified value with colon (":") and no space
        e.g.:

        | Status           | Syntax                |
        |------------------|-----------------------|
        |"out of range"    | "17:22"               |
        |"increasing step" | "1.0:1.5:2.0:2.5:3.0" |
        |"superior than"   | "46"                  |

CSV definition:

    conditions

        * "out of range"
        * "if superior than"
        * "if inferior than"
        * "increasing step"
        * "decreasing step"
