from PySide2.QtCore import QObject, Signal, Slot
import numpy as np
import time


class ClearpathSCSK(QObject):

    print_text_signal = Signal(str)
    connected_signal = Signal(bool)
    homed_signal = Signal(bool)
    move_to_origin_signal = Signal(bool)

    def __init__(self, spindle_pitch_microns=4000, steps_per_revolution=6400, axis_orientation=1):
        QObject.__init__(self)
        try:
            self.pywrapper = __import__('external_libraries.clearpath.clearpathPyWrapper', fromlist='ClearpathTeknicDriver')
        except ImportError:
            print("ImportError")
            return None
        self.scskTeknic = self.pywrapper.ClearpathTeknicDriver()
        self.is_connected = False
        self.ports_count = 0
        self.nodes = []
        self.nodes_id = []
        self.motor_parameters = []
        self.default_parameters = {"spindle_pitch_microns": spindle_pitch_microns,
                                   "steps_per_revolution": steps_per_revolution,
                                   "step_length_microns": spindle_pitch_microns / steps_per_revolution,
                                   "axis_orientation": axis_orientation}

    def get_step_length_microns(self):
        return self.default_parameters.get("step_length_microns")

    def set_node_parameters(self, node=0, port=0, spindle_pitch_microns=4000, steps_per_revolution=6400,
                            axis_orientation=1):
        try:
            if port < self.ports_count and node < self.nodes[port]:
                self.motor_parameters[port][node] = {"spindle_pitch_microns": spindle_pitch_microns,
                                                     "steps_per_revolution": steps_per_revolution,
                                                     "step_length_microns": spindle_pitch_microns / steps_per_revolution,
                                                     "axis_orientation": axis_orientation}
        except Exception as e:
            print(e)
            self.print_text_signal.emit("Selected Node is either busy or disconnected!")
        return

    def connect_motor(self, serial_port=None):
        try:
            is_successful, ports_count, nodes_count, nodes_id, text = self.scskTeknic.connect()
            self.ports_count = ports_count
            self.nodes = nodes_count
            self.nodes_id = nodes_id
            print(is_successful, ports_count, nodes_count, nodes_id, text)
            if is_successful == 1:
                self.is_connected = True
                self.print_text_signal.emit("Connecting to motors...")
                self.connected_signal.emit(True)
                for port in range(ports_count):
                    self.motor_parameters.append([])
                    for node in range(nodes_count[port]):
                        # is_homing = self.home_building_plate(node, port)
                        self.motor_parameters[port].append(self.default_parameters)
                self.print_text_signal.emit("Connection to motors ESTABLISHED!")
                return True, self.ports_count, self.nodes, self.nodes_id
            else:
                self.print_text_signal.emit("Connection to motors NOT established!")
                return False, 0, 0, 0
        except Exception as e:
            print(e)
            self.print_text_signal.emit("exception Connection to motors NOT established!")
            return False, 0, 0, 0

    def disconnect_motor(self):
        try:
            if self.is_connected and self.scskTeknic.close():
                self.print_text_signal.emit("...connection CLOSED!")
                self.connected_signal.emit(False)
                self.is_connected = False
                return True
            else:
                self.print_text_signal.emit("...connection NOT closed!")
                return False
        except Exception as e:
            print(e)
            self.print_text_signal.emit("...connection NOT closed!")
            return False

    def reset_printer(self):
        if self.is_connected:
            try:
                if self.scskTeknic.close():
                    self.disconnect_motor()
                    self.connect_motor()
                    self.print_text_signal.emit("motors status: RESET")
                    return True
                else:
                    return False
            except Exception as e:
                print(e)
                return False

    def __reconnect_printer(self):
        try:
            self.print_text_signal.emit("Reconnecting Clearpath Motor...")
            is_successful, ports_count, nodes_count, nodes_id, text = self.scskTeknic.connect()
            if not is_successful or ports_count != self.ports_count or nodes_count != self.nodes or nodes_id != self.nodes_id:
                self.print_text_signal.emit("...reconnection FAILED!")
                return False
            self.is_connected = True
            self.print_text_signal.emit("...reconnection SUCCESSFUL!")
            self.connected_signal.emit(True)
            return True
        except Exception as e:
            print(e)
            self.print_text_signal.emit("...reconnection FAILED!")
            return False

    def home_motor(self, node=0, port=0, wait_for_motor=False):
        if self.is_connected:
            try:
                node_status = self.scskTeknic.enableNodeMotion(node, port)
                if node_status == 0:
                    return False
                is_valid, message = self.scskTeknic.home(node, port)
                print(node, port, message)
                if is_valid:
                    self.print_text_signal.emit("...homing building plate...")
                    if wait_for_motor:
                        homing_done = False
                        while not homing_done:
                            homing_done = not self.scskTeknic.isHoming(node, port)
                    self.print_text_signal.emit("building plate homed!")
                    self.homed_signal.emit(True)
                    return True
                else:
                    self.print_text_signal.emit("Problems homing building plate!")
                    return False
            except Exception as e:
                print(e)
                return False

    def move_motor(self, distance_mm, feed_rate_mm_min, is_relative=True, node=0, port=0, wait_for_motor=False, safety_check=False, max_checks=5, max_error_mm=0.005):
        if self.is_connected:
            try:
                node_parameters = self.motor_parameters[port][node]
                spindle_pitch_mm = node_parameters.get("spindle_pitch_microns") / 1000.0
                feedrate_rpm = feed_rate_mm_min / spindle_pitch_mm
                if not safety_check:
                    counts = int(node_parameters.get("axis_orientation") * distance_mm * 1000 / node_parameters.get(
                        "step_length_microns"))
                    node_status = self.scskTeknic.enableNodeMotion(node, port)
                    if not node_status:
                        self.print_text_signal.emit("Problems moving node %i!" % node)
                        return False
                    movement_status, expected_time = self.scskTeknic.move(counts, feedrate_rpm, is_relative, node, port)
                    if not movement_status:
                        self.print_text_signal.emit("Problems moving node %i!" % node)
                        return False
                    if wait_for_motor:
                        movement_done = False
                        while not movement_done:
                            movement_done = not self.scskTeknic.isMoving(node, port)
                    self.print_text_signal.emit("Node %i moved!" % node)
                    return True
                else:
                    position_checks = 0
                    start_position = 0
                    while position_checks < max_checks:
                        reconnection_checks = 0
                        reconnection_delay_seconds = 1
                        while not self.is_port_connected(port) and reconnection_checks < max_checks:
                            self.print_text_signal.emit("Attempt %i out of %i to reconnect motors!" % (reconnection_checks + 1, max_checks))
                            time.sleep(reconnection_delay_seconds)
                            self.__reconnect_printer()
                            reconnection_checks += 1
                            reconnection_delay_seconds = min(60, reconnection_delay_seconds * 2)
                            if reconnection_checks == max_checks:
                                self.print_text_signal.emit("FAILED %i out of %i attempts to reconnect motors!" % (reconnection_checks + 1, max_checks))
                                return False
                        if is_relative:
                            start_position = self.print_motor_position(node, port, False)
                        node_status = self.scskTeknic.enableNodeMotion(node, port)
                        counts = int(node_parameters.get("axis_orientation") * distance_mm * 1000 / node_parameters.get(
                            "step_length_microns"))
                        self.scskTeknic.move(counts, feedrate_rpm, is_relative, node, port)
                        if wait_for_motor:
                            movement_done = False
                            while not movement_done:
                                movement_done = not self.scskTeknic.isMoving(node, port)
                        current_position = self.print_motor_position(node, port, False)
                        distance_covered_mm = current_position - start_position
                        if np.abs(distance_covered_mm - distance_mm) < max_error_mm:
                            self.print_text_signal.emit("Node %i moved successfully!" % node)
                            return True
                        else:
                            if self.scskTeknic.hadTorqueSaturation(node, port):
                                self.print_text_signal.emit("Node %i had Torque Saturation!" % node)
                                return False
                            if is_relative:
                                distance_mm = distance_mm - distance_covered_mm
                        position_checks += 1
                    ### If reached this point the buildplate did not reach the position
                    self.print_text_signal.emit("FAILED to move Node %i to desired position!" % node)
                    return False
            except Exception as e:
                print(e)
                return False

    # def move_motor(self, distance_mm, feed_rate_mm_min, is_relative=True, node=0, port=0, wait_for_motor=False, safety_check=False, max_checks=5, max_error_mm=0.005):
    #     if self.is_connected:
    #         try:
    #             node_status = self.scskTeknic.enableNodeMotion(node, port)
    #             if node_status == 0:
    #                 return False
    #             node_parameters = self.motor_parameters[port][node]
    #             spindle_pitch_mm = node_parameters.get("spindle_pitch_microns") / 1000.0
    #             feedrate_rpm = feed_rate_mm_min / spindle_pitch_mm
    #             if not safety_check:
    #                 counts = int(node_parameters.get("axis_orientation") * distance_mm * 1000 / node_parameters.get(
    #                     "step_length_microns"))
    #                 movement_status, expected_time = self.scskTeknic.move(counts, feedrate_rpm, is_relative, node, port)
    #                 if not movement_status:
    #                     return False
    #                 if wait_for_motor:
    #                     movement_done = False
    #                     while not movement_done:
    #                         movement_done = not self.scskTeknic.isMoving(node, port)
    #                 self.print_text_signal.emit("building plate moved!")
    #                 return True
    #             else:
    #                 count_attempts = 0
    #                 start_position = 0
    #                 if is_relative:
    #                     start_position = self.print_motor_position(node, port, False)
    #                 while count_attempts < max_checks:
    #                     counts = int(node_parameters.get("axis_orientation") * distance_mm * 1000 / node_parameters.get(
    #                         "step_length_microns"))
    #                     movement_status, expected_time = self.scskTeknic.move(counts, feedrate_rpm, is_relative, node, port)
    #                     if not movement_status:
    #                         return False
    #                     if wait_for_motor:
    #                         movement_done = False
    #                         while not movement_done:
    #                             movement_done = not self.scskTeknic.isMoving(node, port)
    #                     current_position = self.print_motor_position(node, port, False)
    #                     current_movement = current_position - start_position
    #                     if np.abs(current_movement - distance_mm) < max_error_mm:
    #                         self.print_text_signal.emit("building plate moved!")
    #                         return True
    #                     elif is_relative:
    #                         distance_mm = distance_mm - current_movement
    #                         start_position = current_position
    #                     count_attempts += 1
    #                 return False
    #         except Exception as e:
    #             print(e)
    #             return False

    def print_motor_position(self, node=0, port=0, print=True):
        if self.is_connected:
            count_position = self.scskTeknic.getPosition(node, port)
            node_parameters = self.motor_parameters[port][node]
            position_mm = node_parameters.get("axis_orientation") * count_position * node_parameters.get(
                "step_length_microns") / 1000.0
            if print:
                self.print_text_signal.emit("Motor at node " + str(node) + " and port " + str(port) + " is at:" + str(position_mm) + " mm")
        else:
            self.print_text_signal.emit("The motors are NOT connected!")
        return position_mm

    def stop_motor_movements(self):
        try:
            self.scskTeknic.stopAllMotion()
        except Exception as e:
            raise e

    def is_port_connected(self, port=0):
        if self.is_connected:
            try:
                state = self.scskTeknic.getPortState(port)
                if state != self.scskTeknic.openStates.OPENED_ONLINE:
                    self.is_connected = False
                return self.is_connected
            except Exception as e:
                self.is_connected = False
                return self.is_connected

    @Slot()
    def move_projector(self, distance, feed_rate, relative_move=True):
        self.print_text_signal.emit("Projector movement not supported!")

    @Slot()
    def home_projector(self):
        self.print_text_signal.emit("Projector movement not supported!")

    @Slot()
    def lock_projector(self):
        self.print_text_signal.emit("Projector movement not supported!")