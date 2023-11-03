import string
import random
from django.db import models

# Constants
CODE_LENGTH = 5
CHARACTER_SET = string.ascii_uppercase


def gen_rand_code():
    # return a string made with CHARACTER_SET var of lenghth k
    return ''.join(random.choices(CHARACTER_SET, k=CODE_LENGTH))


def gen_unique_code():
    retries = 10

    for _ in range(retries):
        code = gen_rand_code()
        # if code does not exist in db
        if not Room.objects.filter(code=code).exists():
            return code

    # return error if unique code could not be generated
    raise ValueError(f"Unable to generate a unique code after {retries} retries")


# defining DB table
class Room(models.Model):
    # defining properties
    code = models.CharField(max_length=10, unique=True)
    host = models.CharField(max_length=50, unique=True)
    guest_can_pause = models.BooleanField(null=False, default=False)
    votes_to_skip = models.IntegerField(null=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    cur_song = models.CharField(max_length=50, null=True)

    # custom method to manipulate provided data
    def save(self, *args, **kwargs):
        # if code is empty
        if not self.code:
            # assign a value to code column
            self.code = gen_unique_code()
        # calling default django save method
        super(Room, self).save(*args, **kwargs)
