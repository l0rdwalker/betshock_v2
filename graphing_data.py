import matplotlib.pyplot as plt
import numpy as np
import time
from backend.intergrations.engine.arbie.sports.database.databaseOperations import databaseOperations

database = databaseOperations()


def get_new_data():
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x + np.random.uniform(0, 2*np.pi))
    y2 = np.cos(x + np.random.uniform(0, 2*np.pi))
    return x, y1, y2

x, y1, y2 = get_new_data()

plt.ion() 
fig, ax = plt.subplots()
line1, = ax.plot(x, y1, label='Stream 1')
line2, = ax.plot(x, y2, label='Stream 2')
ax.legend()
plt.show()

def update_plot():
    x, y1, y2 = get_new_data()
    line1.set_ydata(y1)
    line2.set_ydata(y2)
    ax.relim()
    ax.autoscale()
    plt.draw()
    plt.pause(0.1)

# Simulate real-time data update
for _ in range(10):
    update_plot()
    time.sleep(1)  # Simulate delay between data updates

plt.ioff()  # Disable interactive mode
plt.show()
