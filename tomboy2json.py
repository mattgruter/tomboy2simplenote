#!/usr/bin/env python
"""
Created on 2012/01/01

@author: Matthias Grueter <matthias@grueter.name>
@copyright: Copyright (c) 2012 Matthias Grueter
@license: GPL

"""
import datetime
import simplejson as json
import uuid

import dbus
import gobject
import dbus.glib


class TomboyRemoteControl(object):
    def __init__(self):
        pass
        
    def connect(self):
        """Connect to Tomboy's remote control DBUS interface."""
        # get D-Bus session bus
        bus = dbus.SessionBus()
        # access tomboy's D-Bus object
        obj = bus.get_object("org.gnome.Tomboy",
                             "/org/gnome/Tomboy/RemoteControl")
        # save tomboy's remote control interface
        tomboy = dbus.Interface(obj, "org.gnome.Tomboy.RemoteControl")
        self.tomboy = tomboy

    def get_notes(self):
        """Return list of tomboy notes."""
        notes = self.tomboy.ListAllNotes()
        return [self._note2dict(note) for note in notes]
        
    def _parse_contents(self, note):
        #@TODO: handle text formatting and convert it to markdown (parse XML)
        return unicode(self.tomboy.GetNoteContents(note))
        
    def _parse_tags(self, note):
        #@TODO: parse XML to get tags
        return []
        
    def _parse_createdate(self, note):
        ts = self.tomboy.GetNoteCreateDate(note)
        return datetime.datetime.fromtimestamp(ts)
        
    def _parse_modifydate(self, note):
        ts = self.tomboy.GetNoteChangeDate(note)
        return datetime.datetime.fromtimestamp(ts)
        
    def _note2dict(self, note):
        content = self._parse_contents(note)
        tags = self._parse_tags(note)
        createdate = self._parse_createdate(note)
        modifydate = self._parse_modifydate(note)
        systemtags = []
        key = str(uuid.uuid4()) # random string

        return {'content': content,
                'tags': tags,
                'createdate': createdate.strftime('%b %d %Y %H:%M:%S'),
                'modifydate': modifydate.strftime('%b %d %Y %H:%M:%S'),
                'systemtags': systemtags,
                'key': key}


def main():
    tomboy = TomboyRemoteControl()
    tomboy.connect()
    notes = tomboy.get_notes()

    # dump JSON representation of file            
    with open('notes.json', 'w') as fh:
        json.dump(notes, fh)


if __name__ == "__main__":
    import sys
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(None)

