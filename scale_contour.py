import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

def interpolate1d(a, step):
    step = 0.1
    new_a = []
    for i in range(len(a) - 1):
        a1 = a[i]
        a2 = a[i+1]
        diff = a2 - a1
        iters = int(abs(diff) // step)
        for j in range(iters):
            if (diff < 0):
                new_a.append(a1 + (-j * step))
            else:
                new_a.append(a1 + j * step)
    return new_a

def list_linspace(a, num):
    new_len = len(a) * num - num
    new_a = np.zeros(new_len)
    for i in range(len(a) - 1):
        diff = a[i+1] - a[i]
        r = np.linspace(a[i], a[i+1], num)
        if diff == 0:
            print(r)
        for j in range(len(r)):
            new_a[(i * num) + j] = r[j]
    return new_a

def scaled_linspace(a, num):
    a = [i * num for i in a]
    return list_linspace(a, num)


f = open("test.out", "r")
x = []
y = []
for line in f:
    tokens = line.split("\t")
    print(tokens)
    x.append(int(tokens[0]))
    y.append(int(tokens[1]))



x_org = np.copy(x)
y_org = np.copy(y)
num = 2
# Flip coordinates.
plt.gca().invert_yaxis()
x = scaled_linspace(x, num)
y = scaled_linspace(y, num)
r_pos = (x[-1], y[-1])
x_new = np.copy(x[:-1])
y_new = np.copy(y[:-1])
x_new[0] = r_pos[0]
y_new[0] = r_pos[1]
for i in range(1, len(x_new)):
    x_new[i] = x_new[i-1] - (x[i-1] - x[i])
    y_new[i] = y_new[i-1] - (y[i-1] - y[i])
#tck, u = interpolate.splprep([x, y], u=None, s=0, per=1)
#u_new = np.linspace(u.min(), u.max(), 100000)
#new_pts = interpolate.splev(u_new, tck, der=0)
plt.plot(x_new, y_new, 'r--')
plt.plot(r_pos[0], r_pos[1], 'bo')
plt.plot(x[0], y[0], 'go')
plt.plot(x[:-1], y[:-1], 'b--')
plt.plot(x_org[0], y_org[0], 'g*')
plt.plot(x_org[:-1], y_org[:-1], 'b-')
plt.show()
