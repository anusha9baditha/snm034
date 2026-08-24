#H7nK8x
import random
import string
def genotp():
    otp=''
    for i in range(2):
        otp=otp+random.choice(string.ascii_uppercase)+random.choice(string.digits)+random.choice(string.ascii_lowercase) #F7bR8j
    return otp