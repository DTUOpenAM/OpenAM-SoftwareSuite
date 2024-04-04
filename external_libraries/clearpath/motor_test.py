from motors.clearpathSCSK import ClearpathSCSK

if __name__ == "__main__":
    motor = ClearpathSCSK()
    motor.connect_motor()
    building_plate = 0
    wiper = 1
    # Building plate
    motor.set_node_parameters(node=building_plate, spindle_pitch_microns=4000, steps_per_revolution=6400, axis_orientation=-1)
    # Wiper
    motor.set_node_parameters(node=wiper, spindle_pitch_microns=4000, steps_per_revolution=6400, axis_orientation=1)

    motor.disconnect_motor()
    print(motor.scskTeknic.openStates.OPENED_ONLINE)
    print(motor.scskTeknic.getPortState(0))
    print(motor.is_port_connected(0))

