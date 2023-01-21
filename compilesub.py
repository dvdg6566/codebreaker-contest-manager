import io
import time
from datetime import datetime
import subprocess
import awstools
from uuid import uuid4
MAX_ERROR_LENGTH = 500

def check(code, problem_info, userInfo):
    validated = problem_info["validated"]
    nowhitespace = code.replace(" ", "")

    if not validated:
        return {"status":"warning", "message":"Sorry, this problem is still incomplete. Please contact the administrators."}

    if len(code) > 128000:
        return {"status":"danger", "message":"Your code is too long!"}

    return {"status":"success", "message":""}
