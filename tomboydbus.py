#!/usr/bin/env python
"""
Created on 2012/01/01

@author: Matthias Grueter <matthias@grueter.name>
@copyright: Copyright (c) 2012 Matthias Grueter
@license: GPL

"""
import datetime

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
        return self.tomboy.ListAllNotes()

    def get_note_title(self, note):
        """Takes note object and returns its title (unicode string)."""
        title = self.tomboy.GetNoteTitle(note)
        return unicode(title)
        
    def get_note_created_date(self, note):
        """Return creation date as datetime object."""
        date = self.tomboy.GetNoteCreateDate(note)
        return datetime.datetime.fromtimestamp(date)
    
    def get_note_changed_date(self, note):
        """Return last modification date as datetime object."""
        date = self.tomboy.GetNoteChangeDate(note)
        return datetime.datetime.fromtimestamp(date)
        
    def get_note_contents(self, note):
        """Takes note object and return its contents as unicode string."""
        contents = self.tomboy.GetNoteContents(note)
        return unicode(contents)

    def get_note_contents_xml(self, note):
        """Takes note object and return its contents as XML unicode string."""
        xml = self.tomboy.GetNoteContentsXml(note)
        return unicode(xml)
        
    def get_note_xml(self, note):
        """Takes note object and return its XML unicode string representation."""
        xml = self.tomboy.GetNoteCompleteXml(note)
        return unicode(xml)


def write_unicode_to_file(filename, content):
    """Write supplied unicode string to given file (UTF-8 encoded)."""
    with open(filename, 'w') as fh:
        fh.write(content.encode('utf-8'))


def main():
    tomboy = TomboyRemoteControl()
    tomboy.connect()
        
    for i, note in enumerate(tomboy.get_notes()):
        print "Dumping '" + tomboy.get_note_title(note) + "'..."
        
        contents = tomboy.get_note_contents(note)
        write_unicode_to_file(str(i)+".txt", contents)
        
        xml = tomboy.get_note_xml(note)
        write_unicode_to_file(str(i)+".xml", xml)
        
        created = tomboy.get_note_created_date(note)
        changed = tomboy.get_note_changed_date(note)
        filename = str(i) + ".nfo"
        with open(filename, 'w') as fh:
            fh.write(str(created) + '\n' + str(changed))


if __name__ == "__main__":
    import sys
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(None)

