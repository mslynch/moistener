#!/usr/bin/env python3

'''
Script to send a reminder notification based on a message defined in
config.yaml.
'''

import os
import random
import sys
import yaml
from nltk.corpus import wordnet as wn

if sys.platform == 'linux':
    import notify2
elif sys.platform == 'win32':
    import win10toast
elif sys.platform == 'darwin':
    import subprocess


def run():
    '''
    Loads title and message from configuration and calls reminder.
    '''
    print("Ready your canteen...")
    if sys.platform == 'win32':
        config_path = str(os.getenv('APPDATA')) + r'\moistener'
    else:
        config_path = os.path.expanduser('~/.config/moistener')

    with open(config_path + os.sep + 'config.yaml', 'r') as config:
        try:
            data = yaml.load(config)
        except yaml.YAMLError as exc:
            print(exc)
    reminder(data)


def word_from_set(word_type):
    '''
    Returns a random word from a random synset from a WordNet type of word
    (wn.NOUN, wn.ADJ, wn.ADV, wn.VERB)
    '''
    synsets = list(wn.all_synsets(word_type))
    synset = random.choice(synsets)
    lemma = random.choice(synset.lemmas())
    return lemma.name().replace('_', ' ')


def notify_linux(title, message):
    '''
    Sends GTK 3/Qt 4 notification
    '''
    notify2.init('moistener')
    notification = notify2.Notification(title, message, 'important')
    notification.show()


def notify_windows(title, message):
    '''
    Sends a Windows 10 toast notification.
    '''
    win10toast.ToastNotifier().show_toast(title, message, duration=6)


def notify_mac(title, message):
    '''
    Sends a notification through osascript.
    '''
    subprocess.call("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(message, title), shell=True)


def process_string(string):
    '''
    Basic string processing for notification messages. Replaces type-of-word
    codes with randomly selected words from WordNet.
    Accepted values: %NOUN, %ADJ, %ADV, %VERB
    '''
    return string.replace('%NOUN', word_from_set(wn.NOUN)) \
        .replace('%ADJ', word_from_set(wn.ADJ))            \
        .replace('%ADV', word_from_set(wn.ADV))            \
        .replace('%VERB', word_from_set(wn.VERB))


def reminder(data):
    '''
    Creates the notification message and passes it to the correct desktop
    notification function.
    '''
    processed_title = process_string(data['title'])
    processed_message = process_string(data['message'])
    notifiers = {
        'linux': notify_linux,
        'darwin': notify_mac,
        'win32': notify_windows
    }
    print(
        "Notifying with title: " +
        processed_title +
        ", message: " +
        processed_message)
    notifiers[sys.platform](processed_title, processed_message)


if __name__ == '__main__':
    run()
