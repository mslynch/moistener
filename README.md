A friendly reminder script to help you drink more water.

Moistener sends notifications through the OS's desktop notification system. Scheduling is done with cron on Linux and macOS and Task Scheduler on Windows.

Notification messages are fully configurable, with a water reminder and randomly-generated name-calling (via WordNet) suggested as default. Reminder interval is set in minutes.

### Prerequisites
* Python 3
* pip
* Windows 10, macOS, or Linux with Cinnamon, KDE, GNOME, or Xfce

### Installation
```shell
pip3 install -r requirements.txt
python3 install.py
```
Then follow instructions for configuration.

### Notes
A handful of Linux desktop environments are included in ```install.py``` by default. To add another, include its process name in the ```add_cron``` function.
