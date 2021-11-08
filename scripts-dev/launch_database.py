#!/usr/bin/env python
import mailpy.utils

if __name__ == "__main__":
    container = mailpy.utils.MongoContainerManager()
    container.start()
