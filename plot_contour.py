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
        for j in range(len(r)):
            new_a[(i * num) + j] = r[j]
    return new_a

f = open("test.out", "r")
x = []
y = []
for line in f:
    tokens = line.split("\t")
    print(tokens)
    x.append(int(tokens[0]))
    y.append(int(tokens[1]))


# Flip coordinates.
plt.gca().invert_yaxis()
r_pos = (x[-1], y[-1])
x = x[:-1]
y = y[:-1]

#num = 200
#x_new = list_linspace(x, num)
#y_new = list_linspace(y, num)
#tck, u = interpolate.splprep([x, y], u=None, s=0, per=1)
#u_new = np.linspace(u.min(), u.max(), 100000)
#new_pts = interpolate.splev(u_new, tck, der=0)
plt.plot(x, y, 'r--')
plt.plot(r_pos[0], r_pos[1], 'bo')
#plt.plot(new_pts[0], new_pts[1], 'b--')
#print(len(new_pts[1]))
plt.show()
