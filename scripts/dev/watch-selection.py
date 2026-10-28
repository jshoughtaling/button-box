#!/usr/bin/env python3
"""Print the selected contact whenever the switch position (or card) changes.

Run as the service user so the contact store and runtime files are readable:
  sudo -u messagebox python3 watch-selection.py
Card IDs are never printed; only the position, label, and age.
"""

import json
import sys
import time

CONTACTS = "/var/lib/messagebox/state/contacts.json"
SELECTION = "/run/messagebox/nfc-selection.json"
SWITCH_PREFIX = "F0:00:00:"


def load(path):
    try:
        with open(path) as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def describe():
    contacts = load(CONTACTS)
    if contacts is None:
        return "contact store unreadable"
    selection = load(SELECTION)
    if selection is None:
        default = contacts.get("default_recipient")
        label = contacts["contacts"].get(default, {}).get("label")
        return f"nothing selected (default: {label or 'none'})"
    contact = contacts["contacts"].get(selection["jid"])
    label = contact["label"] if contact else "UNKNOWN CONTACT"
    uid = selection["uid"]
    where = ""
    if uid.startswith(SWITCH_PREFIX):
        position = uid[-2:]
        where = "position off" if position == "FF" else f"position {int(position, 16)}"
    return f"{where + ': ' if where else ''}{label}"


last = None
try:
    while True:
        current = describe()
        if current != last:
            print(time.strftime("%H:%M:%S"), current, flush=True)
            last = current
        time.sleep(0.2)
except KeyboardInterrupt:
    sys.exit(0)
