SMS: Spam Mailing Service
============================================================
Python script that monitors PVs EPICS, check their specified operation values and send an e-mail to a list of targets with a warning message if the PV value exceed its limits.

This code reads a list of EPICS PVs and their corresponding specified values
from a MongoDB and monitor them. If any these PVs is not in it's specified
value, an e-mail is sent with a warning message to one or a list of e-mail
address.

So far, it's monitoring the following systems:

    - water temperature of Linac Klystron 1
    - water temperature of Linac Klystron 2
    - water temperature of Linac Accelerating Structures
    - total dose of radiation detectors (Thermo, ELSE, Berthold)

Deploy
------
Environment varibles

|ENV| Default | Desc |
|---|---------|------|
|DB_URL|mongodb://localhost:27017/mailpy-db|MongoDB connection string|

Development
-----------
Install **pre-commit** !

### To do:

    - Signal SMS application to update the entries (Create/Update/Remove)
    - support for condition 'decreasing step' (similar to 'increasing step')
    - supervisory --> PyDM? Web?
    - Consider creating an "user" collection
    - Consider removing the IOC, access via FLASK

Usage
-----

### Include new entries
One could use the rest API and the front-end or by using the `app/utility.py` scripts.

Start an interactive python session at the project root:

```python
import app.utility

app.utility.connect()

# Create a single entry
app.utility.create_entry(...)

# Create entries from a csv file
app.utility.load_csv_table("sms_table.csv")

# Disconnect
app.utility.disconnect()

```

### Syntax:

    - separate e-mails with semicolon (";")
        e.g.: "unknown.user@mail.com;another_user@aMail.com"
    - separate specified value with colon (":")
        e.g.:


| Conditions    | Description  |Syntax                |
|---------------|--------------|----------------------|
|out of range   |              |"17:22"               |
|increasing step|              |"1.0:1.5:2.0:2.5:3.0" |
|superior than  |              |"42"                  |
|inferior than  |              |"46"                  |
