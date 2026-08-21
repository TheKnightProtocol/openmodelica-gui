# OpenModelica Simulation Runner

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.6+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)

A professional desktop application for running OpenModelica simulations with a user-friendly graphical interface. Built with Python and PyQt6, this application simplifies the process of executing compiled OpenModelica models with custom parameters.

## ✨ Features

- 🖥️ **Intuitive GUI**: Clean, modern interface built with PyQt6
- 📁 **File Browser**: Easy selection of OpenModelica executables
- ⏱️ **Time Configuration**: Set start and stop times with spin controls
- ✅ **Input Validation**: Ensures parameters meet requirements (0 ≤ start < stop < 5)
- 📊 **Real-time Output**: View simulation output as it happens
- 🚀 **Process Management**: Robust handling of simulation processes
- 🛡️ **Error Handling**: Comprehensive error detection and user feedback
- 🎨 **Modern Design**: Polished UI with custom styling
- 🔧 **CLI Support**: Run with command-line arguments for automation
- 📝 **Logging**: Detailed output logging for debugging

## 📋 Requirements

| Requirement | Version | Purpose |
|------------|---------|---------|
| Python | 3.6+ | Core runtime |
| PyQt6 | 6.4+ | GUI framework |
| OpenModelica | Latest | Model compilation |
| OS | Windows 10/11 or Linux | Platform |

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/openmodelica-gui.git
cd openmodelica-gui

# Install dependencies
pip install -r requirements.txt
