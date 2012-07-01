# tomboy2simplenote #

*tomboy2simplenote* is a simple script to move [Tomboy](http://projects.gnome.org/tomboy/) notes to [simplenote](http://simplenoteapp.com/). The script exports all Tomboy notes into a single JSON file suitable for simplenote's [import tool](http://simplenote-import.appspot.com/).


## Usage ##
Execute the sript without any arguments. It will create a file 'notes.json' in the current directory.

    ./tomboy2simplenote
    
Any text formatting is converted into markdown syntax recognized by simplenote. Tomboy 'notebook' membership is converted into simplenote 'tags'.
    

## Requirements ##
Python 2.7+ with the following libraries:

- dbus
- gobject
- lxml
