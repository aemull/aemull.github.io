import time
timestamps = [1771261295, 1771261303, 1771261310, 1771261320, 1771261607]
for ts in timestamps:
    dt = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(ts))
    print(f'{ts} --> {dt} UTC')