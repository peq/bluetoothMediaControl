import dbus
import dbus.service
from xml.etree import ElementTree

'''
Some relevant documentation:

Integration into ubuntu media player:
https://specifications.freedesktop.org/mpris-spec/latest/index.html

Dbus tutorial:
https://en.wikibooks.org/wiki/Python_Programming/Dbus
'''

#setup the main glib main loop
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)


class MediaController:
    bus = None
    deviceName = None
    proxy = None
    bus = dbus.SystemBus()
    properties_manager = None
    mediaPlayer = None
    
    print("init")
    
    def __init__(self):
        print("Start init")
        self.bus = dbus.SystemBus()
        self.findDeviceName(self.bus, 'org.bluez', '/org/bluez')
        print("found device " + self.deviceName)
        self.proxy = self.bus.get_object('org.bluez', self.deviceName)
        self.mediaPlayer = dbus.Interface(self.proxy, 'org.bluez.MediaPlayer1')
        # print("props = " + str(self.proxy.getProp("Track")))
        #self.proxy.getTrack(dbus_interface='org.bluez.MediaPlayer1')
        self.properties_manager = dbus.Interface(self.proxy, dbus.PROPERTIES_IFACE)
        track = self.getCurrentTrack()
        print("Keys = " + str(track.keys()))
        print("Album = " + track["Album"])
        print("Artist = " + track["Artist"])
        print("Title = " + track["Title"])
        
        self.properties_manager.connect_to_signal("PropertiesChanged", self.onPropChange)
        
        # self.nextSong()
    def onPropChange(self, iface, props, sig):
        if "Track" in props:
            print("Now playing:")
            print(" Album = " + props["Track"]["Album"])
            print(" Artist = " + props["Track"]["Artist"])
            print(" Title = " + props["Track"]["Title"])
        
    def getCurrentTrack(self):
        return self.properties_manager.Get('org.bluez.MediaPlayer1', 'Track')   

    def findDeviceName(self, bus, service, object_path):
        print("findDeviceName " + object_path)
        if (object_path.endswith("player0")):
            self.deviceName = object_path
            return
        obj = bus.get_object(service, object_path)
        iface = dbus.Interface(obj, dbus.INTROSPECTABLE_IFACE)
        xml_string = iface.Introspect()
        for child in ElementTree.fromstring(xml_string):
            if child.tag == 'node':
                if object_path == '/':
                    object_path = ''
                new_path = '/'.join((object_path, child.attrib['name']))
                self.findDeviceName(bus, service, new_path)

    def nextSong(self):
        self.mediaPlayer.Next()

    def prevSong(self):
        self.mediaPlayer.Previous()    
        
    def pause(self):
        self.mediaPlayer.Pause()    
   
    def play(self):
        self.mediaPlayer.Play()

class PlayerService(dbus.service.Object):
    mediaController = MediaController()
    
    # def __init__(self, mediaController):
    #     path =  "/org/mpris/MediaPlayer2"
    #     dbus.service.Object.__init__(self, dbus.SessionBus(), path)
    
    @dbus.service.method(dbus_interface='org.mpris.MediaPlayer2',
                         in_signature='', out_signature='')
    def Raise(self):
        print("Raise called")
    
    @dbus.service.method(dbus_interface='org.mpris.MediaPlayer2',
                         in_signature='', out_signature='')
    def Quit(self):
        print("Quit called")
    
    @dbus.service.method(dbus_interface='org.mpris.MediaPlayer2.Player',
                         in_signature='', out_signature='')
    def Next(self):
        self.mediaController.nextSong()
        print("calling next")
        
    

if __name__ == '__main__':
    #DBusGMainLoop(set_as_default=True)
    #dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    # mc = MediaController()
    
    session_bus = dbus.SessionBus()
    name = dbus.service.BusName("org.mpris.MediaPlayer2.blue", session_bus)
    ps = PlayerService(session_bus, '/org/mpris/MediaPlayer2')
    
    from gi.repository import GLib

    loop = GLib.MainLoop()
    loop.run()

    # mc.nextSong()                      