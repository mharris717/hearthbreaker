import unittest

class SortThing:
    def __init__(self,num):
        self.num = num

    def get_num(self):
        return self.num

class TestSortThing(unittest.TestCase):
    def test_thing(self):
        a = [SortThing(4),SortThing(3),SortThing(9)]
        b = sorted(a,key=SortThing.get_num)
        self.assertEqual(b[0].num,3)