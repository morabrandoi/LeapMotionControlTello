################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization             #
################################################################################

import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture


class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    
    def add_drone(self, drone):
        self.drone = drone


    def on_init(self, controller):
        print "Initialized"
        self.last_time = {
            "take off": time.time(),
            "motion update": time.time() } # dict
        self.in_flight = False

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP)
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP)
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"


    
        

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        # print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
        #       frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

        

        
        
        # Drone control scheme
        if len(frame.hands) == 1:
            hand = frame.hands[0]
            
            palm_x = hand.palm_position[0]
            palm_y = hand.palm_position[1]
            palm_z = hand.palm_position[2]
            hand_yaw = hand.direction.yaw * Leap.RAD_TO_DEG # yaw in degrees

            # landing and takeoff
            if self.in_flight and False:
                print("finna land")
                self.in_flight = False
                # put in drone landing conidiional based on sphere
            if (not self.in_flight) and (hand.palm_normal.y > 0) and (time.time() - self.last_time["take off"] > 1):
                print("checkppiunt3")
                self.drone.takeoff()
                self.last_time["take off"] = time.time()
                self.in_flight = True
            
            # time limiting
            if time.time() - self.last_time["motion update"] > 0.5:
                self.last_time["motion update"] = time.time()
                
                #update z
                z_dead_min, z_dead_max = -70, 70
                z_min, z_max = -200, 200

                if z_dead_min <= palm_z <= z_dead_max:
                    self.drone.forward(0)
                else:
                    #clip z position to standard range
                    clip_z = max(z_min, min(palm_z, z_max))
                    # mapping speed palm z position to drone speed
                    z_speed = (int)(100 * (abs(clip_z) - z_dead_max) / (z_max - z_dead_max))
                    if palm_z < 0:
                        self.drone.forward(z_speed)
                    else:
                        self.drone.backward(z_speed)

                # update x
                x_dead_min, x_dead_max = -60, 60
                x_min, x_max = -250, 250

                if x_dead_min <= palm_x <= x_dead_max:
                    self.drone.left(0)
                else:
                    #clip x position to standard range
                    clip_x = max(x_min, min(palm_x, x_max))
                    # mapping speed palm x position to drone speed
                    x_speed = (int)(100 * (abs(clip_x) - x_dead_max) / (x_max - x_dead_max))
                    if palm_x < 0:
                        self.drone.left(x_speed)
                    else:
                        self.drone.right(x_speed)
 

                # update y
                # note: mapping pos to throttle speed is different mathematically since position ranges are asymetric
                y_dead_min, y_dead_max = 175, 275
                y_min, y_max = 80, 400

                if y_dead_min <= palm_y <= y_dead_max:
                    self.drone.set_throttle(0)
                else:
                    # negator = 1 if palm_y > (y_dead_max + y_dead_min) / 2 else: -1
                    #clip y position to standard range
                    clip_y = max(y_min, min(palm_y, y_max))
                    # mapping speed palm y position to drone speed
                    if palm_y < (y_dead_max + y_dead_min) / 2: # if y pos is less than "middle"
                        y_speed = (int)(-100 * (clip_y - y_dead_min) / (y_min - y_dead_min) )
                    else:
                        y_speed = (int)(100 * (clip_y - y_dead_max) / (y_max - y_dead_max) )

                    self.drone.set_throttle(y_speed)

                # update yaw
                yaw_dead_min, yaw_dead_max = -40, 40
                yaw_min, yaw_max = -80, 80

                if yaw_dead_min <= hand_yaw <= yaw_dead_max:
                    self.drone.clockwise(0)
                else:
                    #clip yaw position to standard range
                    clip_yaw = max(yaw_min, min(hand_yaw, yaw_max))
                    # mapping speed palm yaw position to drone speed
                    yaw_speed = (int)(100 * (abs(clip_yaw) - yaw_dead_max) / (yaw_max - yaw_dead_max))
                    if hand_yaw < 0:
                        self.drone.counterclockwise(yaw_speed)
                    else:
                        self.drone.clockwise(yaw_speed)

        for hand in frame.hands:

            # self.drone.takeoff()

        


            handType = "Left hand" if hand.is_left else "Right hand"

            # print "  %s, id %d, position: %s" % (
            #     handType, hand.id, hand.palm_position)

                        # we dont need z

            x = hand.palm_position[0]
            y = hand.palm_position[1]
            z = hand.palm_position[2]

            print("hand type: " + handType)
            print("x: %f , y: %f , z: %f " % (x,y,z))

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction
            print("normal: ", normal.x, normal.y, normal.z)
            print("direction: ", direction.x, direction.y, direction.z)
            print("sphere radius", hand.sphere_radius)
            

            # Calculate the hand's pitch, roll, and yaw angles
            print "  pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
                direction.pitch * Leap.RAD_TO_DEG,
                normal.roll * Leap.RAD_TO_DEG,
                direction.yaw * Leap.RAD_TO_DEG)

            # Get arm bone
            # arm = hand.arm
            # print "  Arm direction: %s, wrist position: %s, elbow position: %s" % (
            #     arm.direction,
            #     arm.wrist_position,
            #     arm.elbow_position)

            # Get fingers
            # for finger in hand.fingers:

            #     print "    %s finger, id: %d, length: %fmm, width: %fmm" % (
            #         self.finger_names[finger.type],
            #         finger.id,
            #         finger.length,
            #         finger.width)

            #     # Get bones
            #     for b in range(0, 4):
            #         bone = finger.bone(b)
            #         print "      Bone: %s, start: %s, end: %s, direction: %s" % (
            #             self.bone_names[bone.type],
            #             bone.prev_joint,
            #             bone.next_joint,
            #             bone.direction)

        # Get tools
        # for tool in frame.tools:

        #     print "  Tool id: %d, position: %s, direction: %s" % (
        #         tool.id, tool.tip_position, tool.direction)

        # Get gestures
        for gesture in frame.gestures():
            if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                circle = CircleGesture(gesture)

                # Determine clock direction using the angle between the pointable and the circle normal
                if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2:
                    clockwiseness = "clockwise"
                else:
                    clockwiseness = "counterclockwise"

                # Calculate the angle swept since the last frame
                swept_angle = 0
                if circle.state != Leap.Gesture.STATE_START:
                    previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                    swept_angle =  (circle.progress - previous_update.progress) * 2 * Leap.PI

                print "  Circle id: %d, %s, progress: %f, radius: %f, angle: %f degrees, %s" % (
                        gesture.id, self.state_names[gesture.state],
                        circle.progress, circle.radius, swept_angle * Leap.RAD_TO_DEG, clockwiseness)

            if gesture.type == Leap.Gesture.TYPE_SWIPE:
                swipe = SwipeGesture(gesture)
                print "  Swipe id: %d, state: %s, position: %s, direction: %s, speed: %f" % (
                        gesture.id, self.state_names[gesture.state],
                        swipe.position, swipe.direction, swipe.speed)

            if gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                keytap = KeyTapGesture(gesture)
                print "  Key Tap id: %d, %s, position: %s, direction: %s" % (
                        gesture.id, self.state_names[gesture.state],
                        keytap.position, keytap.direction )

            if gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                screentap = ScreenTapGesture(gesture)
                print "  Screen Tap id: %d, %s, position: %s, direction: %s" % (
                        gesture.id, self.state_names[gesture.state],
                        screentap.position, screentap.direction )

        if not (frame.hands.is_empty and frame.gestures().is_empty):
            print ""

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

