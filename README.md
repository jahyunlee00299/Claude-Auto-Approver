# 🤖 Claude Auto Approver

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

완전 자동화된 터미널 승인 시스템 - PyCharm, CMD, PowerShell 등에서 나타나는 Claude Code 승인 프롬프트를 자동으로 처리합니다.

## ✨ 주요 기능

- 🎯 **완전 자동**: 사용자 Idle 상태 감지 후 자동으로 "1" (Yes) 선택
- 🖥️ **다중 터미널 지원**: PyCharm, CMD, PowerShell, Git Bash, Claude 등
- ⚡ **실시간 모니터링**: 키보드/마우스 활동을 실시간으로 감지
- 🛡️ **중복 방지**: 같은 창에 너무 자주 입력하지 않도록 제어
- 📊 **상세 로깅**: 모든 자동 승인 작업을 시간과 함께 기록
- ⚙️ **커스터마이징**: Idle 시간, 체크 간격 등 자유롭게 설정 가능

## 🚀 빠른 시작

### 설치

```bash
# 저장소 클론
git clone https://github.com/jahyunlee00299/Claude-Auto-Approver.git
cd Claude-Auto-Approver

# 의존성 설치
pip install -r requirements.txt
```

### 기본 사용법

```bash
# 기본 실행 (3초 idle, 0.5초 체크 간격)
python simple_auto_approver.py

# 커스텀 설정으로 실행
python simple_auto_approver.py --idle 5 --interval 1

# 백그라운드 실행 (출력 버퍼링 비활성화)
python -u simple_auto_approver.py --idle 3 --interval 1
```

### 작동 방식

1. **사용자 활동 모니터링**: 키보드와 마우스 입력을 실시간 감지
2. **Idle 상태 감지**: 설정된 시간(기본 3초) 동안 입력이 없으면 Idle로 판단
3. **터미널 확인**: 현재 활성화된 창이 터미널인지 확인
4. **자동 승인**: Idle + 터미널 활성화 = 자동으로 "1" + Enter 입력

### 예시 출력

```
🎯 간단한 자동 승인 시스템
   Idle 임계값: 3초
   체크 간격: 1.0초

✅ 초기화 완료 (Idle 임계값: 3초)
✅ 사용자 활동 모니터링 시작
🔄 모니터링 시작...

💤 Idle 감지 + 터미널 활성화
[12:29:40] ✅ 자동 승인: Claude-Auto-Approver (총 1회)
[12:29:44] 👤 Idle: 0초 | 승인: 1회 | 입력: 2회
```

## 📋 시스템 요구사항

- Python 3.7+
- Windows 10/11
- 필수 패키지:
  - `pywin32` - Windows API 접근
  - `keyboard` - 키보드 입력 모니터링/제어
  - `mouse` - 마우스 활동 모니터링

## ⚙️ 설정 옵션

```bash
python simple_auto_approver.py --help

옵션:
  --idle SECONDS      Idle 임계값 (기본: 3초)
  --interval SECONDS  터미널 체크 간격 (기본: 0.5초)
```

## 📁 프로젝트 구조

```
Claude-Auto-Approver/
├── simple_auto_approver.py  # 메인 자동 승인 프로그램
├── src/
│   ├── auto_approver.py     # 기본 승인 로직
│   └── utils/
│       └── config.py        # 설정 관리
├── requirements.txt         # Python 의존성
└── README.md               # 이 파일
```

## 🎯 모니터링 대상 터미널

- PyCharm
- CMD (명령 프롬프트)
- PowerShell
- Windows Terminal
- Git Bash
- Claude
- Python
- Mintty
- 기타 Terminal

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by automation needs in daily workflows
- Built with Python and love ❤️

## 📞 Contact

- GitHub: [@jahyunlee00299](https://github.com/jahyunlee00299)
- Email: your.email@example.com

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=jahyunlee00299/Claude-Auto-Approver&type=Date)](https://star-history.com/#jahyunlee00299/Claude-Auto-Approver&Date)

---

**⭐ If you find this project useful, please consider giving it a star! ⭐**