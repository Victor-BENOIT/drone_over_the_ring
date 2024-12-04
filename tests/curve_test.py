from djitellopy import Tello
import time

def main():
    # Initialize the Tello drone
    tello = Tello()

    # Connect to the drone
    tello.connect()

    # Take off
    tello.takeoff()

    # Perform a curve maneuver to the point (200, 50, 0)
    tello.curve_xyz_speed(100, 50, 0, 300, 100, 100, 60)

    # Land the drone
    tello.land()

    # End the connection
    tello.end()

if __name__ == "__main__":
    main()