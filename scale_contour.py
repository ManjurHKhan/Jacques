import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

class Transformer:

    def list_linspace(self, a, num):
        new_len = len(a) * num - num
        new_a = np.zeros(new_len)
        for i in range(len(a) - 1):
            diff = a[i+1] - a[i]
            r = np.linspace(a[i], a[i+1], num)
            for j in range(len(r)):
                new_a[(i * num) + j] = r[j]
        return new_a

    def scaled_linspace(self, a, num):
        a = [i * num for i in a]
        return self.list_linspace(a, num)

    def transform(self, path, r_pos, scale):
        x, y = map(list, zip(*path))
        x = self.scaled_linspace(x, scale)
        y = self.scaled_linspace(y, scale)
        x_new = np.copy(x)
        y_new = np.copy(y)
        x_new[0] = r_pos[0]
        y_new[0] = r_pos[1]
        for i in range(1, len(x_new)):
            x_new[i] = x_new[i-1] - (x[i-1] - x[i])
            y_new[i] = y_new[i-1] - (y[i-1] - y[i])
        return zip(x_new, y_new)


f = open("test.out", "r")
x = []
y = []
for line in f:
    tokens = line.split("\t")
    x.append(int(tokens[0]))
    y.append(int(tokens[1]))
x_org = np.copy(x)
y_org = np.copy(y)
num = 2
# Flip coordinates.
plt.gca().invert_yaxis()
t = Transformer()
x = t.scaled_linspace(x, num)
y = t.scaled_linspace(y, num)
r_pos = (x[-1], y[-1])
x_new = np.copy(x[:-1])
y_new = np.copy(y[:-1])
x_new[0] = r_pos[0]
y_new[0] = r_pos[1]
for i in range(1, len(x_new)):
    x_new[i] = x_new[i-1] - (x[i-1] - x[i])
    y_new[i] = y_new[i-1] - (y[i-1] - y[i])
'''
plt.plot(x_new, y_new, 'r--')
plt.plot(r_pos[0], r_pos[1], 'bo')
plt.plot(x[0], y[0], 'go')
plt.plot(x[:-1], y[:-1], 'b--')
plt.plot(x_org[0], y_org[0], 'g*')
plt.plot(x_org[:-1], y_org[:-1], 'b-')
plt.show()
print("shape: ", x_new.shape)
'''
