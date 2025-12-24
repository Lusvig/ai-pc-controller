# 🤖 AI PC Controller

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

> Control your Windows PC using natural language commands powered by FREE AI models.

![Demo](assets/screenshots/demo.gif)

## ✨ Features

### 🎯 Core Features
- **Natural Language Understanding**: Just say or type what you want
- **Voice Control**: Hands-free operation with wake word detection
- **100% Free AI**: Uses Ollama (local), Gemini, or Groq - all free tiers
- **Offline Capable**: Works without internet using Ollama
- **Plugin System**: Extend functionality with custom plugins
- **Macro Recording**: Record and replay complex actions
- **Scheduled Tasks**: Automate recurring commands

### 🖥️ PC Control Capabilities

| Category | Features |
|----------|----------|
| **Applications** | Open, close, switch, minimize, maximize any app |
| **Files** | Create, delete, move, copy, rename, search files |
| **System** | Shutdown, restart, lock, sleep, hibernate |
| **Audio** | Volume control, mute, audio device switching |
| **Display** | Brightness, resolution, multi-monitor |
| **Web** | Open sites, Google search, YouTube playback |
| **Input** | Type text, keyboard shortcuts, mouse control |
| **Clipboard** | Copy, paste, clipboard history |
| **Media** | Play, pause, next, previous track |
| **Network** | WiFi toggle, IP info, speed test |

## 🚀 Quick Start

### Automatic Installation (Recommended)

```batch
# Download and run the installer
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/ai-pc-controller/main/scripts/install.bat
install.bat
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-pc-controller.git
cd ai-pc-controller

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Ollama for free local AI
winget install Ollama.Ollama
ollama pull llama3.2:3b

# Run the application
python -m src.main
```

## 📖 Usage Examples

```
"Open Chrome"
"Search Google for Python tutorials"
"Set volume to 50 percent"
"Take a screenshot"
"Create a folder called Projects on my desktop"
"What's my CPU usage?"
"Lock my computer in 5 minutes"
"Open YouTube and play lofi music"
"Close all browser windows"
"Empty the recycle bin"
```

## ⚙️ Configuration

Edit `config/default_config.yaml`:

```yaml
ai:
  provider: ollama  # ollama, gemini, groq
  model: llama3.2:3b
  
voice:
  enabled: true
  wake_word: "hey computer"
  language: en-US
  
safety:
  confirm_dangerous: true
  dangerous_commands:
    - shutdown
    - delete
    - format
```

## 🔌 Plugins

Create custom plugins in `src/plugins/`:

```python
from src.plugins.plugin_base import PluginBase

class MyPlugin(PluginBase):
    name = "my_plugin"
    
    def get_commands(self):
        return {
            "my_command": self.my_action
        }
    
    def my_action(self, params):
        # Your code here
        pass
```

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md).

## 📄 License

MIT License - see [LICENSE](LICENSE) file.
