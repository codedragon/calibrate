import random
import datetime, threading, time

next_call = time.time()
# create some fake eye data
def create_eye_data(size):
    eye_data = []
    (x, y) = (0.0, 0.0)
    eye_data.append((x, y))
    for i in range(size):
        x = random.uniform(x + 0.5, x - 0.5)
        y = random.uniform(y + 0.5, y - 0.5)
        eye_data.append((x, y))

    return eye_data


def yield_eye_data(origin = []):
    global next_call
    #(x, y) = (0, 0)
    if origin:
        (x, y) = origin
    while True:
        yield x, y
        x = random.uniform(x + 0.03, x - 0.03)
        y = random.uniform(y + 0.03, y - 0.03)
    next_call = next_call + 0.1
    threading.Timer( next_call - time.time(), yield_eye_data ).start()

yield_eye_data()
