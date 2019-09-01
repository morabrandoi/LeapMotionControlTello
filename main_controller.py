from listener import SampleListener
import keyboard as ky
import cv2.cv2 as cv2  # for avoidance of pylint error
import subprocess
import threading
import tellopy
import thread
import numpy
import time
import Leap
import sys
import av



# data handler for tellopy
def data_handler(event, sender, data, **args):
    drone = sender
    if event is drone.EVENT_FLIGHT_DATA:
        print(data)

# keyboard handlers
def press_key_handler(event):
    print(event.name)
    speed = 100
    if event.name == "t":
        drone.takeoff()
    if event.name == "w":
        drone.forward(speed)
    if event.name == "d":
        drone.right(speed)
    if event.name == "s":
        drone.backward(speed)
    if event.name == "a":
        drone.left(speed)
    if event.name == "up":
        drone.set_throttle(speed)
    if event.name == "down":
        drone.set_throttle(-speed)
    if event.name == "left":
        drone.counter_clockwise(speed)
    if event.name == "right":
        drone.clockwise(speed)
    if event.name == "n":
        drone.flip_backright()
    if event.name == "l":
        drone.land()

    if event.name == "q":
        global keep_going
        keep_going = False
        drone.quit()

def release_key_handler(event):
    print(event.name)
    speed = 0
    if event.name == "t":
        drone.takeoff()
    if event.name == "w":
        drone.forward(speed)
    if event.name == "d":
        drone.right(speed)
    if event.name == "s":
        drone.backward(speed)
    if event.name == "a":
        drone.left(speed)
    if event.name == "up":
        drone.set_throttle(speed)
    if event.name == "down":
        drone.set_throttle(-speed)
    if event.name == "left":
        drone.counter_clockwise(speed)
    if event.name == "right":
        drone.clockwise(speed)
    if event.name == "l":
        drone.land()

    if event.name == "q":
        global keep_going
        keep_going = False
        drone.quit()

def start_listener(drone=None):
    # Create a sample listener and controller
    listener = SampleListener() 
    listener.add_drone(drone)
    # listener.__init__(drone)
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press q to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


# event listeners
ky.on_release(release_key_handler, suppress=True)
ky.on_press(press_key_handler, suppress=True)



if subprocess.call(["networksetup -setairportnetwork en0 BrandoTello"] , shell=True) != 0:
    raise ValueError("Network not connected: Turn on copter maybe")

drone = tellopy.Tello()

try:
    drone.subscribe(drone.EVENT_FLIGHT_DATA, data_handler)
    drone.connect()
    drone.wait_for_connection(60.0)

    # skip first 100 frames
    frame_skip = 100
except Exception as e:
    print(e)

# ensuring container initializes
while 1:
    try:
        print("trying video connection")
        container = av.open(drone.get_video_stream())
        container
        break
    except Exception as e:
        print("\n"*100 , "sumthing wen wong xD rawrz", "\n"*2)
        print(e)

        continue

global keep_going
keep_going = True


listener_thread = threading.Thread(target=start_listener, kwargs=dict(drone=drone))
listener_thread.daemon = True
listener_thread.setDaemon(True)
listener_thread.start()




while keep_going:
    for frame in container.decode(video=0):
        if frame_skip > 0:
            frame_skip -= 1
            continue
        start_time = time.time()
        image = cv2.cvtColor(numpy.array(frame.to_image()), cv2.COLOR_RGB2BGR)

        # resizing
        height, width, _ = image.shape
        image = cv2.resize(image, (int(720 * width / height), 720))
        height, width, _ = image.shape

        

        

        cv2.imshow("image", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if frame.time_base < 1.0/60:
            time_base = 1.0/60
        else:
            time_base = frame.time_base
        frame_skip = int((time.time() - start_time)/time_base)
    


cv2.destroyAllWindows()
