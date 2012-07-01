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
import re

import dbus
import gobject
import dbus.glib

import lxml.etree


class Stack(list):
    def __init__(self):
        list.__init__(self)
        
    def push(self, item):
        self.append(item)
        
    def peek(self):
        try:
            return self[-1]
        except IndexError:
            return None
            
    def is_empty(self):
        return len(self) == 0


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
        xmlnote = self.tomboy.GetNoteCompleteXml(note).encode('utf-8')
        parser = lxml.etree.XMLParser(target=MarkdownTarget(), encoding="utf-8")
        return lxml.etree.fromstring(xmlnote, parser)
        
    def _parse_tags(self, note):
        tom_tags = self.tomboy.GetTagsForNote(note)
        tags = [str(tag).split(':')[-1] for tag in tom_tags]
        return tags
        
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

        
class MarkdownTarget(object):

    TAGS = ('normal', 'large', 'huge', 'small', 'monospace',
            'bold', 'italic', 'highlight', 'strikethrough',
            'list', 'list-item',
            'url',
            'note-content')

    def __init__(self):
        self.events = Stack()
        self.result = u''
        self.indent = ''

    def start(self, tag, attrib):
        tag = re.sub('{.+}', '', tag)   # remove namespace from tag
        
        if tag == 'list':
            self.result += '\n'
            if self.events.peek() =='list-item':
                self.indent += '\t'
            
        self.events.push(tag)
    
    def data(self, text):
        tag = self.events.pop()
        if tag in self.TAGS:
            if tag == 'huge':
                self.result += '## %s ##\n' % text
            elif tag == 'large':
                self.result += '### %s ###\n' % text
            elif tag == 'monospace':
                self.result += '\t%s' % text   
            elif tag in ('bold', 'italic', 'highlight'):
                self.result += '*%s*' % text
            elif tag == 'url':
                self.result += '<%s>' % text
            elif tag == 'list-item':
                self.result += '%s- %s\n' % (self.indent, text)
            
            else:
                self.result += text
        self.events.push(tag)
    
    def end(self, endtag):
        endtag = re.sub('{.+}', '', endtag)   # remove namespace from tag
        tag= self.events.pop()
        assert tag == endtag, 'opening & closing tags must match'
        
        if tag == 'list' and self.events.peek() =='list-item':
            self.indent = self.indent[:-1]  
        
    def close(self):
        assert self.events.is_empty(), 'all XML tags must be closed'
        
        # finishing touches: first line is title, replace tabs with spaces
        doc = re.sub('(?P<title>.+)\n',
                     '# \g<title> #\n', self.result, count=1)
        doc = doc.replace('\t', '    ')
        doc = re.sub('\n\*(?P<subtitle>.+)\*\n',
                     '\n#### \g<subtitle> ####\n', doc)

        # reset parser
        self.context = Stack()
        self.result = ''
        self.indent = ''
        
        return doc


def main():
    tomboy = TomboyRemoteControl()
    tomboy.connect()
    notes = tomboy.get_notes()

    # dump JSON representation to file            
    with open('notes.json', 'w') as fh:
        json.dump(notes, fh)


if __name__ == "__main__":
    import sys
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(None)

