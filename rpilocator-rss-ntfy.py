#!/usr/bin/env python3

import requests
import feedparser
import time
import os
import signal
import sys

FEED_URL = os.getenv("FEED_URL", "https://rpilocator.com/feed/")
NTFY_BASE_URL = os.getenv("NTFY_BASE_URL", "https://ntfy.sh")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")
NTFY_PRIORITY = os.getenv("NTFY_PRIORITY", "default")
NTFY_EMOJI = os.getenv("NTFY_EMOJI", "white_check_mark")
INITIAL_NOTIFICATION = os.getenv("INITIAL_NOTIFICATION", "False").lower() == "true"

MESSAGE_TITLE = "xlocator Stock Alert"
USER_AGENT = "xlocator feed alert"


# Create the message body
def formatMessage(entry):
    message = entry.title + "\n\n" + "Link: " + entry.link

    return message


# Send the push/message to all devices connected to ntfy
def sendMessage(message):
    headers = {"Title": MESSAGE_TITLE, "Priority": NTFY_PRIORITY, "Tags": NTFY_EMOJI}

    try:
        req = requests.post(
            url=NTFY_BASE_URL + "/" + NTFY_TOPIC,
            data=message,
            headers=headers,
            timeout=20,
        )
    except requests.exceptions.Timeout:
        print("Request Timeout")
        pass
    except requests.exceptions.TooManyRedirects:
        print("Too many requests")
        pass
    except requests.exceptions.RequestException as e:
        print(e)
        pass


def handle_shutdown(signal, *_):
    print(f"Caught signal {signal}, shutting down")
    sys.exit(1)


print("Starting rpilocator")
print("Configuration")
print(f"  FEED_URL: {FEED_URL}")
print(f"  NTFY_BASE_URL: {NTFY_BASE_URL}")
print(f"  NTFY_TOPIC: {NTFY_TOPIC}")
print(f"  NTFY_PRIORITY: {NTFY_PRIORITY}")
print(f"  NTFY_EMOJI: {NTFY_EMOJI}")
print(f"  INITIAL_NOTIFICATION: {INITIAL_NOTIFICATION}")
print(f"  MESSAGE_TITLE: {MESSAGE_TITLE}")
print(f"  USER_AGENT: {USER_AGENT}")
print()

if not NTFY_TOPIC:
    print("NTFY_TOPIC is required but not set")
    sys.exit(1)

# Catch SIGTERM so that we can shut down when `docker stop` is called.
signal.signal(signal.SIGTERM, handle_shutdown)

# Set control to blank list
control = []

# Fetch the feed
f = feedparser.parse(FEED_URL, agent=USER_AGENT)

# If there are entries in the feed, add entry guid to the control variable
if f.entries:
    for entries in f.entries:
        if INITIAL_NOTIFICATION == True:
            message = formatMessage(entries)
            sendMessage(message)
        control.append(entries.id)

# Only wait 30 seconds after initial run.
time.sleep(30)

while True:
    # Fetch the feed again, and again, and again...
    f = feedparser.parse(FEED_URL, agent=USER_AGENT)

    # Compare feed entries to control list.
    # If there are new entries, send a message/push
    # and add the new entry to control variable
    for entries in f.entries:
        if entries.id not in control:
            message = formatMessage(entries)

            sendMessage(message)

            # Add entry guid to the control variable
            control.append(entries.id)

    time.sleep(59)
