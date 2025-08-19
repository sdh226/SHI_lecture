import math

STANDARD_POWERS = [7.5, 11, 15, 18.5, 22, 30, 37, 45, 55, 75, 90, 110, 132, 160, 200, 250, 315, 400, 500]

def pick_standard_power_kw(p_kw):
    for p in STANDARD_POWERS:
        if p >= p_kw:
            return p
    return STANDARD_POWERS[-1]

def size_hoist_motor(
    load_ton,
    speed_m_per_min,
    drum_diameter_m=1.2,
    reeving=4,                    # 줄수(rope parts)
    t_acc=3.0,                    # 가속시간(s)
    dyn_coeff=1.15,               # 동적계수(부두용 1.05~1.15 예시)
    reeving_eff=0.94,             # 도르래/로프 효율(전체)
    gearbox_eff=0.95,
    bearing_eff=0.98,
    radius_layer_factor=1.00,     # 로프 상부층 반경 고려(>=1.0)
    motor_rpm=1750,               # 4극 모터 @60Hz
    service_factor=1.10           # 모터 여유
):
    g = 9.81
    m = load_ton * 1000.0
    v_hook = speed_m_per_min / 60.0                  # m/s
    r_eff = (drum_diameter_m * radius_layer_factor) / 2.0
    a = v_hook / t_acc if t_acc and t_acc > 0 else 0 # m/s²

    # 훅 측 설계힘(출력 산정용): 가속도 + 동적계수
    F_hook = m * (g + a) * dyn_coeff                 # N

    # 줄수/도르래 손실 반영한 드럼 라인텐션
    T_line = F_hook / (reeving * reeving_eff)        # N

    # 드럼 토크/속도
    T_drum = T_line * r_eff                          # N·m
    omega_drum = (reeving * v_hook) / r_eff          # rad/s

    # 드럼→모터
    P_drum = T_drum * omega_drum                     # W
    eta_mech = gearbox_eff * bearing_eff
    P_motor = (P_drum / eta_mech) * service_factor   # W
    P_motor_kw = P_motor / 1000.0

    omega_motor = 2 * math.pi * motor_rpm / 60.0
    gear_ratio = omega_motor / omega_drum
    T_motor = (T_drum / (gear_ratio * gearbox_eff)) * service_factor

    return {
        "hook_force_N": F_hook,
        "drum_torque_Nm": T_drum,
        "drum_speed_rads": omega_drum,
        "motor_power_kw": P_motor_kw,
        "selected_power_kw": pick_standard_power_kw(P_motor_kw),
        "gear_ratio": gear_ratio,
        "motor_torque_Nm": T_motor
    }
