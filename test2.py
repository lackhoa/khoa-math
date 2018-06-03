from itertools import *


class c:
    def get_x(self):
        if more_than_one(self.y) or more_than_one(self.z):
            return range(10)
        else:
            return next(iter(self.z)) - next(iter(self.y))

    def get_y(self):
        if more_than_one(self.x) or more_than_one(self.z):
            return self.y
        else:
            return next(iter(self.z)) - next(iter(self.x))

    def get_z(self):
        if more_than_one(self.x) or more_than_one(self.y):
            return self.z
        else:
            return next(iter(self.x)) + next(iter(self.y)


def more_than_one(gen):
    try:
        g = iter(gen)
        ng = next(g)
        nng = next(g)
        return True
    except StopIteration:
        return False


