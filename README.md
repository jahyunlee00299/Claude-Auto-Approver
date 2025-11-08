# 🤖 Claude Auto Approver

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

Intelligent automation tool for automatic approval prompts with smart pattern detection, OCR, and context-aware responses.

## ✨ Features

- 🎯 **Smart Pattern Detection**: Automatically detects approval prompts and dialogs
- 🖼️ **OCR Support**: Reads text from images and screenshots
- 🔄 **Context-Aware**: Understands different types of approval scenarios
- ⚡ **Fast Response**: Instant approval with customizable delays
- 🛡️ **Safe Mode**: Preview actions before execution
- 📊 **Logging**: Detailed activity logs for audit trails

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/jahyunlee00299/Claude-Auto-Approver.git
cd Claude-Auto-Approver

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

### Basic Usage

```python
from auto_approver import AutoApprover

# Initialize the approver
approver = AutoApprover()

# Start monitoring for approval prompts
approver.start()

# Stop monitoring
approver.stop()
```

## 📋 Requirements

- Python 3.7+
- Windows 10/11 (Linux/Mac support coming soon)
- Dependencies listed in `requirements.txt`

## 🛠️ Configuration

Create a `config.yaml` file in the project root:

```yaml
# config.yaml
settings:
  auto_approve: true
  delay_seconds: 1
  safe_mode: false
  log_level: INFO

patterns:
  - "Do you want to approve"
  - "Click OK to continue"
  - "Confirm action"
```

## 📁 Project Structure

```
Claude-Auto-Approver/
├── src/
│   ├── main.py           # Main application entry point
│   ├── auto_approver.py  # Core approval logic
│   ├── pattern_detector.py # Pattern matching engine
│   └── utils/            # Utility functions
├── tests/               # Unit tests
├── docs/               # Documentation
├── scripts/            # Helper scripts
├── requirements.txt    # Python dependencies
├── setup.py           # Package setup
├── config.yaml        # Configuration file
└── README.md         # This file
```

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