# qB-Queueᴹᴱᵀᴬ
**Queue-Based Metadata Exception & Temporary Access Manager for qBittorrent**

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

*The intent is to automatically weed out queued torrents that would otherwise stall on metaDL, also useful displaying the size of all torrents in the queue*

*Personally using with [decluttarr](https://github.com/ManiMatter/decluttarr/) and [qbittorrent-totals](https://github.com/KaiStarkk/qbittorrent-totals)*

## Demo
### Before:
![before_screenshot](https://github.com/user-attachments/assets/a913808b-5a02-4916-ba6b-2d45fc6dfb6f)
### During:
![during_screenshot](https://github.com/user-attachments/assets/f0ebe124-a72f-4288-b6bf-0fca56042c94)
### After:
![after_screenshot](https://github.com/user-attachments/assets/ec0fcf37-d352-4632-ad8a-23f2e9e6ff9c)
### Logs:
![logs_screenshot](https://github.com/user-attachments/assets/1db4dcce-db69-4752-ba04-020e3816df58)


## ✨ Features
- 🚀 **Metadata Priority Boosting** - Temporarily bypass active download limits for metadata retrieval
- ⚖️ **Queue Equilibrium** - Automatically restores original queue positions post-metadata acquisition
- 🔒 **API-First Design** - Non-intrusive WebUI integration
- ⏱️ **Configurable Polling** - Adjustable check interval (default: 60s)
- 📜 **YAML Configuration** - Simple declarative setup
- 🛡️ **Systemd Integration** - Production-grade service management
- 📊 **Verbose Logging** - Detailed operational insights

## 📦 Installation
```bash
git clone https://github.com/AdamWHY2K/qB-QueueMETA.git
mv qB-QueueMETA /opt/
cd /opt/qB-QueueMETA
pip install -r requirements.txt
```

## ⚙️ Configuration
```bash
nano config.yaml
```
### Configuration Reference
| Key                 | Type    | Default | Description                                           |
|---------------------|---------|---------|-------------------------------------------------------|
| `host`              | string  | **Required** | qBittorrent WebUI endpoint (host:port)                |
| `username`          | string  | `""`    | WebUI authentication username                         |
| `password`          | string  | `""`    | WebUI authentication password                         |
| `interval`          | integer | `60`    | Polling interval in seconds               |
| `once`              | boolean | `false` | Single execution mode                   |
| `verbose`           | boolean | `false` | Enable debug logging                                  |
| `verify_certificate`| boolean | `true`  | SSL validation (May need to disable if using self-signed certs)                            |

## 🚀 Usage
```bash
python3 qB-QueueMETA.py --config config.yaml [--host] [--username] [--password] [--interval]
```

## 🖥️ Systemd Service
```bash
sudo systemctl edit qB-QueueMETA --full --force
```
```systemd
[Unit]
Description=qB-Queueᴹᴱᵀᴬ - Metadata Exception & Temporary Access for qBittorrent torrents.
After=network.target qbittorrent.service
StartLimitIntervalSec=1d
StartLimitBurst=10

[Service]
Type=simple
User=qbittorrent-nox
SyslogIdentifier=qB-QueueMETA
WorkingDirectory=/opt/qB-QueueMETA/
ExecStart=/usr/bin/python3 /opt/qB-QueueMETA/qB-QueueMETA.py --config /opt/qB-QueueMETA/config.yaml
Restart=on-failure
RestartSec=3600s

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl start qB-QueueMETA.service
sudo systemctl status qB-QueueMETA.service
sudo systemctl enable qB-QueueMETA.service
```

## 🚨 Troubleshooting
```bash
# View service logs
sudo journalctl -u qb-queuemeta.service -f

# Test qBittorrent API accessibility
curl -v host:port/api/v2/app/preferences

# Test configuration
python3 qB-QueueMETA.py --config config.yaml --verbose
```

## 🤝 Contributing
PRs welcome! Please follow:
1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Add changes (`git add .`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push branch (`git push origin feature/amazing-feature`)
6. Open PR

## 📜 License
This project is licensed under the **GNU Affero General Public License v3.0**.  
This means:
- You can use, modify, and distribute this software freely
- **You must disclose source code** of any modified versions
- Network services using this code must provide source to users
- All derivative works must remain under AGPLv3

Full license text available in [LICENSE](https://raw.githubusercontent.com/AdamWHY2K/qB-QueueMETA/refs/heads/main/LICENSE) file.

Disclaimer: This project is not affiliated with qBittorrent or its developers. Use at your own risk.
