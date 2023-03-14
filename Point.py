import numpy as np

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if other is None:
            return False
        return abs(self.x - other.x) < 10**(-5) and abs(self.y - other.y) < 10**(-5)
    
    def __repr__(self):
        return "(" + str(round(self.x, 3)) + ", " + str(round(self.y, 3)) + ")"

    @staticmethod
    def distance(p1, p2):
        return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)


if __name__ == "__main__":
    p0 = Point(0, 0)
    p1 = Point(0, 0)

    a = [p0, p1]
    b = [p0, p1]
    print(a[0] == b[0])