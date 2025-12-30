# FocusTimer - 스마트 뽀모도로 타이머 🎓

생산성 향상을 위한 **지능형 뽀모도로 타이머**입니다. 단순한 타이머를 넘어, 사용자의 집중 주기를 고려한 **스마트 세션 플래닝** 기능을 제공합니다.

## ✨ 주요 기능

### 1. 스마트 세션 플래닝 (Smart Session Planner)
사용자가 가용한 시간(예: 60분, 120분)을 입력하면, 최적의 집중-휴식 사이클을 자동으로 생성합니다.
- **초기 적응 (Standrad Focus)**: 부담 없는 **25분** 집중으로 시작하여 뇌를 예열합니다.
- **피크 몰입 (Deep Focus)**: 집중도가 높아지는 시점에 맞춰 **35분** 내외의 긴 집중 시간을 배정합니다.
- **유동적 휴식**: 세션 길이에 따라 5분 또는 10분의 적절한 휴식을 배치합니다.
- **마무리 (Wrap-up)**: 남은 자투리 시간은 가볍게 정리할 수 있도록 배정합니다.

### 2. 강력한 타이머 기능
- **오버타임(Overtime) 추적**: 타이머가 끝나도 바로 끊기지 않고, 얼마나 더 초과해서 집중했는지(또는 쉬었는지) 보여줍니다. 흐름을 끊지 않고 자연스럽게 다음 단계로 넘어갈 수 있습니다.
- **집중 방해 기록 (Distraction Log)**: 집중 중 딴짓을 하거나 방해를 받았다면 "I got distracted" 버튼을 클릭하세요. 로그(`focus_log.csv`)에 기록되어 나중에 분석할 수 있습니다.

### 3. 편의 기능
- **시스템 트레이 최소화**: 창을 닫거나 최소화하면 트레이 아이콘으로 숨어들어 작업 표시줄을 차지하지 않습니다.
- **Always on Top**: 타이머 종료 시 화면 최상단으로 올라와 확실하게 알려줍니다.

---

## 🚀 설치 및 실행

### 1. 실행 파일 다운로드 (Windows)
`dist/main.exe` 파일을 다운로드하여 실행하면 별도의 파이썬 설치 없이 바로 사용할 수 있습니다.
*(참고: 직접 빌드하려면 아래 컴파일 방법을 참고하세요)*

### 2. 소스 코드로 실행
Python 3.8 이상이 필요합니다.

```bash
# 1. 저장소 클론
git clone https://github.com/ParkSeongGyeol/13_pomodoro.git
cd 13_pomodoro

# 2. 의존성 설치
pip install -r requirements.txt
# (또는 pip install pillow pystray)

# 3. 실행
python main.py
```

---

## 🛠️ 컴파일 방법 (Build Instructions)

이 프로젝트는 속도 최적화와 용량 경량화를 위해 **Nuitka**를 사용하여 C언어 기반의 실행 파일로 컴파일할 수 있습니다.

### 사전 준비
1. **Nuitka 설치**:
   ```bash
   pip install nuitka
   ```
2. **C 컴파일러**: Nuitka는 C 컴파일러가 필요합니다. (자동으로 MinGW 등을 다운로드 하거나 Visual Studio Build Tools를 사용합니다.)

### 빌드 명령어
터미널(Powershell 권장)에서 아래 명령어를 실행하세요.

python -m nuitka --assume-yes-for-downloads --standalone --onefile --enable-plugin=tk-inter --windows-console-mode=disable --include-data-file=assets/icon.ico=assets/icon.ico --windows-icon-from-ico=assets/icon.ico main.py


- `--standalone`: 독립 실행형 배포
- `--onefile`: 단일 `.exe` 파일로 생성
- `--enable-plugin=tk-inter`: Tkinter UI 지원 활성화
- `--windows-console-mode=disable`: 실행 시 검은색 콘솔 창 숨기기

빌드가 완료되면 `main.exe` 파일이 생성됩니다.

---

## 📂 파일 구조
- `main.py`: 애플리케이션 진입점 및 UI 로직 (Tkinter)
- `planner.py`: 스마트 스케줄 생성 알고리즘 (핵심 로직)
- `tests/`: 단위 테스트 폴더
  - `test_planner.py`: 스케줄링 알고리즘 테스트
  - `test_pomodoro.py`: 타이머 로직 테스트

---

## 📝 라이선스
MIT License

## 👨‍💻 작성자
ParkSeongGyeol
