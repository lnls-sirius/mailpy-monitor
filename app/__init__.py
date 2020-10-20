import multiprocessing

SMS_MAX_QUEUE_SIZE = 50000
SMS_QUEUE = multiprocessing.Queue(maxsize=SMS_MAX_QUEUE_SIZE)
IOC_MAX_QUEUE_SIZE = 50000
IOC_QUEUE = multiprocessing.Queue(maxsize=IOC_MAX_QUEUE_SIZE)

STS = "-Sts"
SEL = "-Sel"

SMS_PREFIX = "SMS"
SMS_ENABLE_PV = SMS_PREFIX + ":Scanning:Enable"

SMS_ENABLE_PV_STS = SMS_ENABLE_PV + STS
SMS_ENABLE_PV_SEL = SMS_ENABLE_PV + SEL

ENABLE_SEL = f"Enable{SEL}"
ENABLE_STS = f"Enable{STS}"
