# https://stackoverflow.com/questions/63994574/why-does-importing-a-file-from-a-folder-work-but-calling-a-file-from-an-importe
# Allows AWS tools files to be imported

from . import sts
from . import users
from . import cognito
from . import problems
from . import awshelper
from . import submissions
from . import announcements