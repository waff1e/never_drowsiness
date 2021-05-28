from mibandAPI import *
import threading
import time
import asyncio

print("HELLO WORLD")
miband = mibandAPI("DB:28:14:20:F4:D0", "c2fa26313cba3df7cf0fe85f0e41dfe2")
t = time.time()
async def looper():
    global t
    while True:
        miband.get_realtime()
        currentHeartRate = int(miband.loadHeartRate())
        if currentHeartRate != 0:
            print(currentHeartRate())
        
        if (time.time() - t >= 12):
            miband.requestHeartRate()
            t = time.time()

async def main():
    print("GET BAND FILE")
    future = asyncio.ensure_future(looper())
    print("기다리십쇼 국민여러분 기다리십쇼")
    asyncio.sleep(3)
    while True:
        #print("나는 빡빡이다")
        #asyncio.sleep(3)
        pass

    #future.cancel() # Cancel Async



miband.initHeartRate()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
# miband.initHeartRate()

# t = time.time()

# def heartRateTimer():
#     global t
#     timer = threading.Timer(0.01, heartRateTimer)
#     timer.name = "Detector_Timer"
#     #timer.daemon = True
   
#     currentHeartRate = int(miband.loadHeartRate())
#     if currentHeartRate != 0:
#         print(currentHeartRate)

#     if (time.time() - t >= 12):
#         miband.requestHeartRate()
#         t = time.time()

#     timer.start()

# heartRateTimer()


