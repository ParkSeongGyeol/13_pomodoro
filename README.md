# FocusTimer - 뽀모도로 타이머

생산성 향상을 위한 뽀모도로 기법 기반 시간 관리 도구입니다.

## 기능

- ⏱️ **뽀모도로 타이머**: 25분 작업 + 5분 휴식 사이클
- 📊 **작업 로그**: CSV 형식으로 작업 기록 저장
- 🎯 **계획 관리**: 일일 계획 수립 및 관리
- 🔔 **알림**: 작업 시간 종료 시 알림

## 설치

### 요구사항
- Python 3.8 이상
- tkinter (일반적으로 Python에 포함됨)

### 설치 방법

```bash
git clone https://github.com/ParkSeongGyeol/13_pomodoro.git
cd 13_pomodoro
pip install -r requirements.txt
```

## 사용 방법

```bash
python main.py
```

## 파일 구조

- `main.py` - 메인 애플리케이션 파일
- `planner.py` - 계획 관리 모듈
- `tests/` - 테스트 파일
  - `test_pomodoro.py` - 뽀모도로 타이머 테스트
  - `test_planner.py` - 계획 관리 테스트

## 테스트 실행

```bash
python -m pytest tests/
```

## 라이선스

MIT License

## 작성자

ParkSeongGyeol
