import math

def calculate_hoist_motor_specifications(load_ton, speed_m_per_min, drum_diameter_m=1.0):
    """
    갠트리 크레인 권상 모터 사양 계산 (DNV 규정 적용)
    
    Parameters:
    - load_ton: 하중 (톤)
    - speed_m_per_min: 권상 속도 (m/min)
    - drum_diameter_m: 드럼 직경 (m), 기본값 1.0m
    
    Returns:
    - dict: 모터 사양 계산 결과
    """
    
    # 기본 상수들
    g = 9.81  # 중력가속도 (m/s²)
    rope_efficiency = 0.95  # 로프 효율
    gearbox_efficiency = 0.95  # 기어박스 효율
    bearing_efficiency = 0.98  # 베어링 효율
    
    # DNV 안전율 (DNV-OS-D101 기준)
    dnv_safety_factor = 2.0  # DNV 권상 시스템 안전율
    dynamic_load_factor = 1.3  # 동적 하중 계수
    marine_environment_factor = 1.2  # 해상 환경 계수
    
    # 단위 변환
    load_kg = load_ton * 1000
    load_n = load_kg * g
    speed_m_per_sec = speed_m_per_min / 60
    
    print("=== 거제조선소 갠트리 크레인 권상모터 설계 계산 ===")
    print(f"하중: {load_ton} ton ({load_kg} kg)")
    print(f"권상속도: {speed_m_per_min} m/min ({speed_m_per_sec:.3f} m/s)")
    print(f"드럼직경: {drum_diameter_m} m")
    print()
    
    return {
        'load_n': load_n,
        'speed_m_per_sec': speed_m_per_sec,
        'drum_diameter_m': drum_diameter_m,
        'dnv_safety_factor': dnv_safety_factor,
        'dynamic_load_factor': dynamic_load_factor,
        'marine_environment_factor': marine_environment_factor,
        'rope_efficiency': rope_efficiency,
        'gearbox_efficiency': gearbox_efficiency,
        'bearing_efficiency': bearing_efficiency
    }

def calculate_required_torque(specs):
    """
    필요 토크 계산
    """
    load_n = specs['load_n']
    drum_diameter_m = specs['drum_diameter_m']
    dnv_safety_factor = specs['dnv_safety_factor']
    dynamic_load_factor = specs['dynamic_load_factor']
    marine_environment_factor = specs['marine_environment_factor']
    rope_efficiency = specs['rope_efficiency']
    
    # 드럼 반지름
    drum_radius_m = drum_diameter_m / 2
    
    # 기본 토크 계산
    basic_torque = load_n * drum_radius_m
    
    # DNV 안전율 적용
    design_torque = basic_torque * dnv_safety_factor * dynamic_load_factor * marine_environment_factor
    
    # 효율 고려
    required_torque = design_torque / rope_efficiency
    
    print("=== 토크 계산 ===")
    print(f"기본 토크: {basic_torque:.2f} N·m")
    print(f"DNV 안전율: {dnv_safety_factor}")
    print(f"동적 하중 계수: {dynamic_load_factor}")
    print(f"해상 환경 계수: {marine_environment_factor}")
    print(f"설계 토크 (안전율 적용): {design_torque:.2f} N·m")
    print(f"필요 토크 (효율 고려): {required_torque:.2f} N·m")
    print()
    
    return required_torque

def calculate_motor_power(specs, required_torque):
    """
    모터 출력 계산
    """
    speed_m_per_sec = specs['speed_m_per_sec']
    drum_diameter_m = specs['drum_diameter_m']
    gearbox_efficiency = specs['gearbox_efficiency']
    bearing_efficiency = specs['bearing_efficiency']
    
    # 드럼 각속도 계산 (rad/s)
    drum_angular_velocity = (2 * speed_m_per_sec) / drum_diameter_m
    
    # 기계적 출력 계산
    mechanical_power = required_torque * drum_angular_velocity
    
    # 전체 효율
    total_efficiency = gearbox_efficiency * bearing_efficiency
    
    # 필요 모터 출력 (W)
    motor_power_w = mechanical_power / total_efficiency
    
    # kW 변환
    motor_power_kw = motor_power_w / 1000
    
    # 상용 모터 사이즈로 반올림 (다음 표준 사이즈)
    standard_powers = [7.5, 11, 15, 18.5, 22, 30, 37, 45, 55, 75, 90, 110, 132, 160, 200, 250, 315, 400, 500]
    selected_power_kw = next(power for power in standard_powers if power >= motor_power_kw)
    
    print("=== 출력 계산 ===")
    print(f"드럼 각속도: {drum_angular_velocity:.3f} rad/s")
    print(f"기계적 출력: {mechanical_power:.2f} W ({mechanical_power/1000:.2f} kW)")
    print(f"전체 효율: {total_efficiency:.3f}")
    print(f"필요 모터 출력: {motor_power_kw:.2f} kW")
    print(f"선정 모터 출력: {selected_power_kw} kW")
    print()
    
    return motor_power_kw, selected_power_kw

def calculate_gear_ratio(specs, selected_power_kw):
    """
    기어비 계산
    """
    speed_m_per_sec = specs['speed_m_per_sec']
    drum_diameter_m = specs['drum_diameter_m']
    
    # 일반적인 모터 회전수 (4극 모터 기준)
    motor_rpm = 1750  # rpm
    motor_angular_velocity = (2 * math.pi * motor_rpm) / 60  # rad/s
    
    # 드럼 각속도
    drum_angular_velocity = (2 * speed_m_per_sec) / drum_diameter_m
    
    # 기어비 계산
    gear_ratio = motor_angular_velocity / drum_angular_velocity
    
    print("=== 기어비 계산 ===")
    print(f"모터 회전수: {motor_rpm} rpm")
    print(f"모터 각속도: {motor_angular_velocity:.2f} rad/s")
    print(f"드럼 각속도: {drum_angular_velocity:.3f} rad/s")
    print(f"필요 기어비: {gear_ratio:.1f}:1")
    print()
    
    return gear_ratio

def marine_environment_considerations():
    """
    해상 환경 고려사항
    """
    print("=== 해상 환경 고려사항 ===")
    print("1. 내염성 요구사항:")
    print("   - 모터 외함: IP65 이상 (방진/방수)")
    print("   - 권상기: 스테인리스 스틸 또는 내식성 코팅")
    print("   - 베어링: 내식성 그리스 사용")
    print()
    print("2. 진동 대책:")
    print("   - 진동 등급: IEC 60034-14 기준 Class R (Reinforced)")
    print("   - 방진 마운팅 시스템 적용")
    print("   - 균형 등급: G2.5 이하")
    print()
    print("3. 온도 조건:")
    print("   - 운전 온도: -20°C ~ +40°C")
    print("   - 절연 등급: Class F 이상 권장")
    print()
    print("4. DNV 인증 요구사항:")
    print("   - DNV-GL 타입 승인 필요")
    print("   - 선급 검사 대응")
    print("   - 품질 문서 제출 (Mill Certificate 등)")
    print()

def generate_motor_specification_summary(load_ton, speed_m_per_min, required_torque, 
                                       motor_power_kw, selected_power_kw, gear_ratio):
    """
    최종 모터 사양 요약
    """
    print("=== 최종 모터 사양 요약 ===")
    print(f"적용 하중: {load_ton} ton")
    print(f"권상 속도: {speed_m_per_min} m/min")
    print(f"필요 토크: {required_torque:.0f} N·m")
    print(f"필요 출력: {motor_power_kw:.1f} kW")
    print(f"선정 출력: {selected_power_kw} kW")
    print(f"기어비: {gear_ratio:.1f}:1")
    print()
    print("권장 모터 사양:")
    print(f"- 3상 유도전동기, {selected_power_kw}kW, 1750rpm")
    print("- 절연등급: Class F")
    print("- 보호등급: IP65")
    print("- 진동등급: Class R (IEC 60034-14)")
    print("- 인증: DNV-GL Type Approval")
    print("- 적용: 해상 크레인용 (Marine Duty)")
    print()

def main():
    """
    메인 계산 함수
    """
    # 입력 조건
    load_ton = 50  # 하중 (ton)
    speed_m_per_min = 10  # 권상속도 (m/min)
    drum_diameter_m = 1.2  # 드럼직경 (m) - 일반적인 50톤급 크레인 드럼
    
    # 1. 기본 사양 계산
    specs = calculate_hoist_motor_specifications(load_ton, speed_m_per_min, drum_diameter_m)
    
    # 2. 토크 계산
    required_torque = calculate_required_torque(specs)
    
    # 3. 출력 계산
    motor_power_kw, selected_power_kw = calculate_motor_power(specs, required_torque)
    
    # 4. 기어비 계산
    gear_ratio = calculate_gear_ratio(specs, selected_power_kw)
    
    # 5. 해상 환경 고려사항
    marine_environment_considerations()
    
    # 6. 최종 사양 요약
    generate_motor_specification_summary(load_ton, speed_m_per_min, required_torque,
                                       motor_power_kw, selected_power_kw, gear_ratio)

if __name__ == "__main__":
    main()