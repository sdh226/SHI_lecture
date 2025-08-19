import math
import numpy

def calculate_torque(force, radius, efficiency):
    torque = force*radius/efficiency
    return torque

def calculate_torque_kg(mass, radius, efficiency):
    force = mass * 9.81
    if efficiency <= 0:
        print("효율값이 잘못되었습니다.")
        return None
    torque = force*radius/efficiency
    return torque

def calculate_power(torque_nm, speed_rpm):
    speed = speed_rpm * 2 * math.pi / 60 # rad/s 로 변환
    power = torque_nm*speed/1000  # kW로 변환
    return power 

def calculate_n_optimal(J_load, J_motor):
    n_optimal = math.sqrt(J_load/J_motor)
    return n_optimal

def calculate_n_critical(J_load, J_motor):
    n_critical = math.sqrt(J_load/J_motor/10)
    return n_critical

def calculate_RMS_torque(time_series, torque_series):
    return math.sqrt(sum(torque_series**2*time_series)/sum(time_series))

def main():
    force = 25000 # kgf -> Nm
    rpm = 1800  # rpm
    radius = 12 # m
    efficiency = 0.85
    safety_factor = 1.2 # DNV 규정 적용
    load_inertia = 4250 # kgm^2
    motor_intertia = 125 # kgm^2



    torque = calculate_torque(force, radius, efficiency) * safety_factor
    power = calculate_power(torque, rpm)
    n_optimal = calculate_n_optimal(load_inertia, motor_intertia)
    n_critical = calculate_n_critical(load_inertia, motor_intertia)

    time_series = numpy.array([3, 2, 1, 3, 2, 1])
    torque_series = numpy.array([900, 600, 0, 300, 600, 0])
    RMS_torque = calculate_RMS_torque(time_series, torque_series)
    
    print(f"계산된 토크는 {torque:.1f} Nm 입니다. ")
    print(f"계산된 파워는 {power:.1f} kW입니다.")
    print(f"최적의 감속비는 {n_optimal:.1f}:1 입니다.")
    print(f"최소 감속비는 {n_critical:.1f}:1 입니다.")
    print(f"계산된 RMS토크는 {RMS_torque:.1f}　Nm 입니다.")
    pass

if __name__ == "__main__":
    
    
    main()