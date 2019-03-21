
test = [1,2]
PV = {}
# CON Mail Server
PREFIX = "CMS:PV"
# create PVs
#==============================================================================
SUFIX = ["MinValue", "MaxValue", "Timeout"]
for i in range(len(test)):
    for j in range(len(SUFIX)):
        aux = {
            PREFIX + str(i+1) + ":" + SUFIX[j] : {
                'type' : 'int'
            }
        }
        print(aux)
        PV.update(aux)
#==============================================================================
for i in range(len(test)):
    aux = {
        PREFIX + str(i+1) + ":Condition" : {
            'type' : 'enum'
        }
    }
    print(aux)
    PV.update(aux)
#==============================================================================
for i in range(len(test)):
    aux = {
        PREFIX + str(i+1) + ":EGU" : {
            'type' : 'enum'
        }
    }
    print(aux)
    PV.update(aux)
