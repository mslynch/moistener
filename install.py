#!/usr/bin/env python3

'''
Install script for moistener. Creates a config.yaml and saves moistener.py the
OS's autostart directory (or an alternate directory if specified).
'''

import getpass
import os
import stat
import subprocess
import sys
import shutil
import nltk
import yaml
if sys.platform == 'darwin' or sys.platform == 'linux':
    from crontab import CronTab


def main():
    '''
    Prompts user for notification schedule and allows moistener to run on startup.
    '''
    install_paths = {
        'linux': os.path.expanduser('~/.moistener'),
        'darwin': os.path.expanduser('~/.moistener'),
        'win32': str(os.getenv('LOCALAPPDATA')) + r'\moistener'
    }
    config_paths = {
        'linux': os.path.expanduser('~/.config/moistener'),
        'darwin': os.path.expanduser('~/.config/moistener'),
        'win32': str(os.getenv('APPDATA')) + r'\moistener'
    }

    print("Adding Moistener to startup...")

    nltk.download('wordnet')

    print(
        "Moistener uses WordNet to generate random words. The following  "
        "symbols will be replaced at runtime with words from their "
        "respective categories:\n"
        "%NOUN, %ADJ, %ADV, %VERB")

    default_title = "Drink some water!"
    title = input(
        "Enter notification title (leave blank for '" +
        default_title + "'): ")
    if title == '':
        title = default_title

    default_message = "Drink some water, you %ADJ %NOUN."
    message = input(
        "Enter notification message (leave blank for '" +
        default_message + "'): ")
    if message == '':
        message = default_message

    interval = input(
        "Enter reminder interval in minutes (leave blank for 15): ")
    if interval == '':
        interval = '15'

    cfg_dict = {'title': title, 'message': message}

    py_loc = add_exec(install_paths[sys.platform], 'moistener.py')

    add_config(config_paths[sys.platform], cfg_dict)

    if sys.platform == 'win32':
        add_scheduled_task(py_loc, interval)
    elif sys.platform == 'linux':
        add_cron(py_loc, interval)
    else:
        add_cron(py_loc, interval)

    print("Installation complete.")


def add_exec(path, filename):
    '''
    Copies executable to the given path.
    '''
    if not os.path.exists(path):
        os.makedirs(path)
    exec_loc = path + os.sep + filename
    shutil.copyfile(filename, exec_loc)
    # make file executable
    os_stat = os.stat(exec_loc)
    os.chmod(exec_loc, os_stat.st_mode | stat.S_IEXEC)
    print("File created: " + exec_loc)
    return exec_loc


def add_config(cfg_path, cfg_dict):
    '''
    Creates the configuration file and saves it to the given path.
    '''
    if not os.path.exists(cfg_path):
        os.makedirs(cfg_path)
    cfg_loc = cfg_path + os.sep + 'config.yaml'
    with open(cfg_loc, 'w') as cfg_file:
        yaml.dump(cfg_dict, cfg_file, default_flow_style=False)
    print("File created: " + cfg_loc)


def add_scheduled_task(install_path, interval):
    '''
    Creates or updates an existing Windows Task Scheduler task for moisturizer.
    Documentation for schtasks is available at:
    https://msdn.microsoft.com/en-us/library/windows/desktop/bb736357(v=vs.85).aspx
    '''
    # delete = 'schtasks /Delete /TN moistener /F'
    query = 'schtasks /Query /TN moistener'
    query_ret_code = subprocess.call(query)

    moistener_task = 'schtasks /Create' +                                                   \
        ' /TN moistener ' +                                                                 \
        ' /RU ' + getpass.getuser() +                                                       \
        ' /SC MINUTE ' +                                                                    \
        ' /MO ' + interval +                                                                \
        ' /TR "' + sys.executable.replace('python', 'pythonw') + ' ' + install_path + '"' + \
        '" /F'
    if query_ret_code != 0:
        moistener_task = moistener_task.replace('/Create', '/Change')
    moistener_ret_code = subprocess.call(moistener_task)
    if moistener_ret_code != 0:
        raise Exception(
            "Return code of " +
            str(moistener_ret_code) +
            " from schtasks call!")

    print('Task scheduled!')


def add_cron(py_loc, interval):
    '''
    Adds moistener.py to the user's crontab.
    '''
    cron = CronTab(user=True)
    cron.remove_all(comment='moistener')
    if sys.platform == 'linux':
        cron_command = 'export $(egrep -z DBUS_SESSION_BUS_ADDRESS /proc/$( ' + \
            'pgrep -u "$LOGNAME" cinnamon-session || ' +                        \
            'pgrep -u "$LOGNAME" kdeinit || ' +                                 \
            'pgrep -u $LOGNAME gnome-session || ' +                             \
            'pgrep -u "$LOGNAME" gnome-shell || ' +                             \
            'pgrep -u "$LOGNAME" xfce4-session' +                               \
            ')/environ) && DISPLAY=:0 ' + py_loc
    else:
        cron_command = py_loc
    job = cron.new(
        command=cron_command,
        comment='moistener')
    job.minute.every(int(interval))
    cron.write()
    print("Scheduled cron job!")


if __name__ == '__main__':
    main()
