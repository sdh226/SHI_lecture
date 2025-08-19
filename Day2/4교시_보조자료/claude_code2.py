"""
조선업 모터 계산 시스템 v2.0
삼성중공업/현대중공업 등 조선소 실무 환경용

주요 기능:
- 윈치/크레인 모터 토크 및 출력 계산
- 최적/최소 감속비 계산
- RMS 토크 분석
- DNV/ABS/KR 규정 적용
- 해상 환경 보정 계수 적용

Author: Marine Engineering Team
Date: 2025.08.19
"""

import math
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ClassificationSociety(Enum):
    """선급 규정 열거형"""
    DNV = "DNV"
    ABS = "ABS" 
    KR = "KR"
    BV = "BV"
    LR = "LR"


class MarineEnvironment(Enum):
    """해상 환경 분류"""
    COASTAL = "연안"
    OFFSHORE = "근해"
    DEEP_SEA = "원해"
    ARCTIC = "북극해"
    TROPICAL = "열대해"


@dataclass
class MotorSpecification:
    """모터 사양 데이터 클래스"""
    load_capacity_ton: float
    operating_speed_rpm: float
    drum_radius_m: float
    system_efficiency: float
    safety_factor: float
    load_inertia_kgm2: float
    motor_inertia_kgm2: float
    environment: MarineEnvironment
    classification: ClassificationSociety


@dataclass
class CalculationResult:
    """계산 결과 데이터 클래스"""
    required_torque_nm: float
    motor_power_kw: float
    optimal_gear_ratio: float
    minimum_gear_ratio: float
    rms_torque_nm: Optional[float] = None
    environmental_corrections: Optional[Dict[str, float]] = None


class MarineMotorCalculator:
    """조선업 모터 계산 전문 클래스"""
    
    # 클래스 상수 정의
    GRAVITY_ACCELERATION = 9.81  # m/s²
    KGF_TO_NEWTON = 9.81
    RPM_TO_RADIAN_PER_SEC = 2 * math.pi / 60
    WATT_TO_KILOWATT = 1000
    
    # DNV/ABS 안전율 기준
    SAFETY_FACTORS = {
        ClassificationSociety.DNV: 2.0,
        ClassificationSociety.ABS: 2.2,
        ClassificationSociety.KR: 2.0,
        ClassificationSociety.BV: 2.0,
        ClassificationSociety.LR: 2.0
    }
    
    # 해상 환경 보정 계수
    ENVIRONMENTAL_CORRECTIONS = {
        MarineEnvironment.COASTAL: {"salt": 1.15, "temp": 1.05, "vibration": 1.05},
        MarineEnvironment.OFFSHORE: {"salt": 1.20, "temp": 1.08, "vibration": 1.10},
        MarineEnvironment.DEEP_SEA: {"salt": 1.10, "temp": 1.15, "vibration": 1.08},
        MarineEnvironment.ARCTIC: {"salt": 1.05, "temp": 1.20, "vibration": 1.15},
        MarineEnvironment.TROPICAL: {"salt": 1.25, "temp": 1.25, "vibration": 1.12}
    }

    def __init__(self, specification: MotorSpecification):
        """
        초기화 메서드
        
        Args:
            specification: 모터 사양 객체
        """
        self.spec = specification
        self._validate_inputs()
        logger.info(f"모터 계산기 초기화: {specification.environment.value} 환경, {specification.classification.value} 규정")

    def _validate_inputs(self) -> None:
        """입력값 유효성 검증"""
        validations = [
            (self.spec.load_capacity_ton > 0, "하중 용량은 0보다 커야 합니다"),
            (self.spec.operating_speed_rpm > 0, "운전 속도는 0보다 커야 합니다"),
            (self.spec.drum_radius_m > 0, "드럼 반지름은 0보다 커야 합니다"),
            (0 < self.spec.system_efficiency <= 1, "시스템 효율은 0과 1 사이여야 합니다"),
            (self.spec.safety_factor > 1, "안전율은 1보다 커야 합니다"),
            (self.spec.load_inertia_kgm2 > 0, "부하 관성은 0보다 커야 합니다"),
            (self.spec.motor_inertia_kgm2 > 0, "모터 관성은 0보다 커야 합니다"),
            (self.spec.drum_radius_m <= 5.0, "드럼 반지름이 비현실적으로 큽니다 (5m 초과)")
        ]
        
        for condition, message in validations:
            if not condition:
                logger.error(f"입력값 검증 실패: {message}")
                raise ValueError(message)

    def calculate_basic_torque(self, force_n: float) -> float:
        """
        기본 토크 계산
        
        Args:
            force_n: 힘 (Newton)
            
        Returns:
            float: 기본 토크 (N·m)
        """
        if force_n <= 0:
            raise ValueError("힘은 0보다 커야 합니다")
            
        basic_torque = force_n * self.spec.drum_radius_m / self.spec.system_efficiency
        logger.debug(f"기본 토크 계산: {basic_torque:.2f} N·m")
        return basic_torque

    def calculate_torque_from_mass(self, mass_kg: float) -> float:
        """
        질량으로부터 토크 계산
        
        Args:
            mass_kg: 질량 (kg)
            
        Returns:
            float: 토크 (N·m)
        """
        force_n = mass_kg * self.GRAVITY_ACCELERATION
        return self.calculate_basic_torque(force_n)

    def calculate_power_requirement(self, torque_nm: float) -> float:
        """
        필요 출력 계산
        
        Args:
            torque_nm: 토크 (N·m)
            
        Returns:
            float: 출력 (kW)
        """
        angular_velocity_rad_per_sec = self.spec.operating_speed_rpm * self.RPM_TO_RADIAN_PER_SEC
        power_w = torque_nm * angular_velocity_rad_per_sec
        power_kw = power_w / self.WATT_TO_KILOWATT
        
        logger.debug(f"출력 계산: {power_kw:.2f} kW (토크: {torque_nm:.2f} N·m, 속도: {self.spec.operating_speed_rpm} rpm)")
        return power_kw

    def calculate_optimal_gear_ratio(self) -> float:
        """
        최적 감속비 계산
        
        Returns:
            float: 최적 감속비
        """
        if self.spec.motor_inertia_kgm2 <= 0:
            raise ValueError("모터 관성은 0보다 커야 합니다")
            
        optimal_ratio = math.sqrt(self.spec.load_inertia_kgm2 / self.spec.motor_inertia_kgm2)
        logger.debug(f"최적 감속비: {optimal_ratio:.2f}:1")
        return optimal_ratio

    def calculate_minimum_gear_ratio(self) -> float:
        """
        최소 감속비 계산 (10배 관성비 기준)
        
        Returns:
            float: 최소 감속비
        """
        optimal_ratio = self.calculate_optimal_gear_ratio()
        minimum_ratio = optimal_ratio / math.sqrt(10)
        logger.debug(f"최소 감속비: {minimum_ratio:.2f}:1")
        return minimum_ratio

    def calculate_rms_torque(self, time_series: np.ndarray, torque_series: np.ndarray) -> float:
        """
        RMS 토크 계산
        
        Args:
            time_series: 시간 배열
            torque_series: 토크 배열
            
        Returns:
            float: RMS 토크 (N·m)
        """
        if len(time_series) != len(torque_series):
            raise ValueError("시간 배열과 토크 배열의 길이가 다릅니다")
        
        if len(time_series) == 0:
            raise ValueError("빈 배열은 처리할 수 없습니다")
            
        # 유효한 값만 필터링
        valid_indices = ~(np.isnan(time_series) | np.isnan(torque_series))
        if not np.any(valid_indices):
            raise ValueError("유효한 데이터가 없습니다")
            
        time_valid = time_series[valid_indices]
        torque_valid = torque_series[valid_indices]
        
        total_time = np.sum(time_valid)
        if total_time == 0:
            raise ValueError("총 시간이 0입니다")
            
        weighted_torque_squared = np.sum(torque_valid**2 * time_valid)
        rms_torque = math.sqrt(weighted_torque_squared / total_time)
        
        logger.debug(f"RMS 토크: {rms_torque:.2f} N·m")
        return rms_torque

    def apply_environmental_corrections(self, base_torque: float) -> Tuple[float, Dict[str, float]]:
        """
        환경 보정 계수 적용
        
        Args:
            base_torque: 기본 토크
            
        Returns:
            Tuple[float, Dict[str, float]]: (보정된 토크, 보정 계수 딕셔너리)
        """
        corrections = self.ENVIRONMENTAL_CORRECTIONS[self.spec.environment]
        
        # 각 보정 계수 적용
        salt_corrected = base_torque * corrections["salt"]
        temp_corrected = salt_corrected * corrections["temp"]
        final_corrected = temp_corrected * corrections["vibration"]
        
        correction_summary = {
            "염분_보정": corrections["salt"],
            "온도_보정": corrections["temp"],
            "진동_보정": corrections["vibration"],
            "총_보정": corrections["salt"] * corrections["temp"] * corrections["vibration"]
        }
        
        logger.info(f"환경 보정 적용: {correction_summary['총_보정']:.3f}배 증가")
        return final_corrected, correction_summary

    def get_classification_safety_factor(self) -> float:
        """
        선급 규정에 따른 안전율 반환
        
        Returns:
            float: 안전율
        """
        return self.SAFETY_FACTORS.get(self.spec.classification, 2.0)

    def perform_comprehensive_calculation(self, 
                                        time_series: Optional[np.ndarray] = None,
                                        torque_series: Optional[np.ndarray] = None) -> CalculationResult:
        """
        종합 계산 수행
        
        Args:
            time_series: 시간 배열 (선택적)
            torque_series: 토크 배열 (선택적)
            
        Returns:
            CalculationResult: 계산 결과 객체
        """
        try:
            # 1. 기본 토크 계산
            load_force_n = self.spec.load_capacity_ton * 1000 * self.GRAVITY_ACCELERATION
            basic_torque = self.calculate_basic_torque(load_force_n)
            
            # 2. 환경 보정 적용
            env_corrected_torque, env_corrections = self.apply_environmental_corrections(basic_torque)
            
            # 3. 안전율 적용
            classification_safety = self.get_classification_safety_factor()
            final_torque = env_corrected_torque * classification_safety * self.spec.safety_factor
            
            # 4. 출력 계산
            power_kw = self.calculate_power_requirement(final_torque)
            
            # 5. 감속비 계산
            optimal_gear = self.calculate_optimal_gear_ratio()
            minimum_gear = self.calculate_minimum_gear_ratio()
            
            # 6. RMS 토크 계산 (선택적)
            rms_torque = None
            if time_series is not None and torque_series is not None:
                rms_torque = self.calculate_rms_torque(time_series, torque_series)
            
            result = CalculationResult(
                required_torque_nm=final_torque,
                motor_power_kw=power_kw,
                optimal_gear_ratio=optimal_gear,
                minimum_gear_ratio=minimum_gear,
                rms_torque_nm=rms_torque,
                environmental_corrections=env_corrections
            )
            
            logger.info("종합 계산 완료")
            return result
            
        except Exception as e:
            logger.error(f"계산 중 오류 발생: {str(e)}")
            raise


def generate_detailed_report(spec: MotorSpecification, result: CalculationResult) -> str:
    """
    상세 계산 보고서 생성
    
    Args:
        spec: 모터 사양
        result: 계산 결과
        
    Returns:
        str: 보고서 문자열
    """
    report = f"""
{'='*80}
조선업 모터 계산 결과 보고서
{'='*80}

📋 입력 조건:
   하중 용량: {spec.load_capacity_ton:,.1f} 톤
   운전 속도: {spec.operating_speed_rpm:,} rpm
   드럼 반지름: {spec.drum_radius_m:.2f} m
   시스템 효율: {spec.system_efficiency:.1%}
   운용 환경: {spec.environment.value}
   적용 선급: {spec.classification.value}

📊 계산 결과:
   필요 토크: {result.required_torque_nm:,.0f} N·m
   모터 출력: {result.motor_power_kw:,.1f} kW
   최적 감속비: {result.optimal_gear_ratio:.1f}:1
   최소 감속비: {result.minimum_gear_ratio:.1f}:1

🌊 환경 보정 계수:
"""
    
    if result.environmental_corrections:
        for key, value in result.environmental_corrections.items():
            report += f"   {key}: {value:.3f}\n"
    
    if result.rms_torque_nm:
        report += f"\n📈 RMS 토크: {result.rms_torque_nm:.1f} N·m\n"
    
    # 권장사항 추가
    report += f"""
💡 설계 권장사항:
   - 모터 용량: {result.motor_power_kw * 1.1:.0f} kW 이상 (10% 여유율)
   - 기어박스 용량: {result.required_torque_nm * 1.2:,.0f} N·m 이상 (20% 여유율)
   - 관성비 검토: {spec.load_inertia_kgm2/spec.motor_inertia_kgm2:.1f}:1 (권장: 10:1 이하)

⚠️  주의사항:
   - 해상 환경 보정계수 적용됨
   - 정기적인 토크 모니터링 필요
   - 극한 날씨 시 운전 제한 고려

{'='*80}
"""
    return report


def main():
    """메인 실행 함수 - 실무 예제"""
    
    # 실제 조선소 프로젝트 예제
    print("🏗️ 삼성중공업 컨테이너선 윈치 모터 계산 예제\n")
    
    # 모터 사양 정의
    container_ship_winch = MotorSpecification(
        load_capacity_ton=50.0,          # 50톤 윈치
        operating_speed_rpm=1800,        # 1800 rpm
        drum_radius_m=1.2,               # 1.2m 반지름 (지름 2.4m)
        system_efficiency=0.85,          # 85% 효율
        safety_factor=1.2,               # 추가 안전율
        load_inertia_kgm2=4250,         # 부하 관성
        motor_inertia_kgm2=125,         # 모터 관성
        environment=MarineEnvironment.OFFSHORE,  # 근해 환경
        classification=ClassificationSociety.DNV  # DNV 규정
    )
    
    try:
        # 계산기 초기화
        calculator = MarineMotorCalculator(container_ship_winch)
        
        # 시계열 데이터 (실제 운전 패턴)
        operating_time = np.array([10, 5, 3, 10, 5, 2])  # 초
        operating_torque = np.array([120000, 80000, 0, 50000, 80000, 0])  # N·m
        
        # 종합 계산 수행
        result = calculator.perform_comprehensive_calculation(
            time_series=operating_time,
            torque_series=operating_torque
        )
        
        # 상세 보고서 출력
        report = generate_detailed_report(container_ship_winch, result)
        print(report)
        
        # 추가 분석
        print("🔍 추가 분석:")
        print(f"   전력 소비량: {result.motor_power_kw * 24:.0f} kWh/일 (24시간 운전 시)")
        print(f"   연간 전력비: {result.motor_power_kw * 24 * 365 * 0.1:.0f} USD (0.1$/kWh 기준)")
        
        # 다른 환경에서의 비교
        print("\n🌍 환경별 비교:")
        environments = [MarineEnvironment.COASTAL, MarineEnvironment.DEEP_SEA, MarineEnvironment.ARCTIC]
        
        for env in environments:
            temp_spec = MotorSpecification(
                load_capacity_ton=50.0, operating_speed_rpm=1800, drum_radius_m=1.2,
                system_efficiency=0.85, safety_factor=1.2, load_inertia_kgm2=4250,
                motor_inertia_kgm2=125, environment=env, classification=ClassificationSociety.DNV
            )
            temp_calc = MarineMotorCalculator(temp_spec)
            temp_result = temp_calc.perform_comprehensive_calculation()
            
            print(f"   {env.value}: {temp_result.required_torque_nm:,.0f} N·m, {temp_result.motor_power_kw:.1f} kW")
        
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류: {str(e)}")
        print(f"❌ 오류 발생: {str(e)}")


if __name__ == "__main__":
    main()