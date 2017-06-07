import time

nums = range(100)

a = 1

try:
    for i in nums:
        print(i)
        a = i
        time.sleep(1)
except KeyboardInterrupt:
    print('异常终止')
    print(a)

