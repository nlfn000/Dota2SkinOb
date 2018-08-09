import threading
import time


class A:
    valueA = 213

    def __init__(self):
        print('A')


class X:
    valueX = 450

    def __init__(self):
        print('X')


class B(A):
    def __init__(self):
        super().__init__()
        print('B')


class C(B):
    def __init__(self):
        super().__init__()
        print('C')


class D(B, X):
    def __init__(self):
        super().__init__()


test = D()
print(test.valueX)
test2 = D()
test2.valueX = 123344
print(test2.valueX)
print(test.valueX)
print('fak')
