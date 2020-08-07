#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import wx
import wx.adv
from datetime import datetime
import socks
import socket
from threading import Thread
from cryptography.fernet import Fernet
import tor
from locale import getdefaultlocale as language
from googletrans import Translator
from random import randint

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        self.nickname = "{0}{1}".format("guest", randint(100, 900))
        self.enableEncryption = False
        self.enableTranslate = False
        self.tObj = None
        self.fObj = None
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((800, 580))
        self.list_box_connection_history = wx.ListBox(self, wx.ID_ANY, choices=[""])
        self.text_nickname = wx.TextCtrl(self, wx.ID_ANY, self.nickname)
        self.bitmap_button_nickname = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap("img\\set-nickname-btn.jpg", wx.BITMAP_TYPE_ANY))
        self.text_host = wx.TextCtrl(self, wx.ID_ANY, "localhost")
        self.bitmap_button_host = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap("img\\connect-btn.jpg", wx.BITMAP_TYPE_ANY))
        self.text_fernet = wx.TextCtrl(self, wx.ID_ANY, Fernet.generate_key())
        self.bitmap_button_fernet = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap("img\\message-encryption-btn.jpg", wx.BITMAP_TYPE_ANY))
        self.list_box_messages = wx.ListBox(self, wx.ID_ANY, choices=[])
        self.text_send_message = wx.TextCtrl(self, wx.ID_ANY, "Hello", style=wx.TE_PROCESS_ENTER)
        self.text_send_message.Bind(wx.EVT_TEXT_ENTER, self.SendBtn)
        self.bitmap_button_send = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap("img\\send-btn.jpg", wx.BITMAP_TYPE_ANY))
        self.bitmap_button_message_encryption = wx.BitmapButton(self, wx.ID_ANY, wx.Bitmap("img\\message-translation-btn.jpg", wx.BITMAP_TYPE_ANY))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.SetNicknameBtn, self.bitmap_button_nickname)
        self.Bind(wx.EVT_BUTTON, self.ConnectBtn, self.bitmap_button_host)
        self.Bind(wx.EVT_BUTTON, self.MessageEncryptionBtn, self.bitmap_button_fernet)
        self.Bind(wx.EVT_BUTTON, self.SendBtn, self.bitmap_button_send)
        self.Bind(wx.EVT_BUTTON, self.EnableTranslationBtn, self.bitmap_button_message_encryption)

        with open("connection-history.log", "r") as r:
            for x in r.readlines():
                self.list_box_connection_history.InsertItems([x], 0)
            r.close()




    if tor.CheckInstall():
        if not(tor.CheckRunning()):
            tor.RunTor()
    else:
        tor.InstallTor()
        tor.RunTor()


    def runServer(self):

        global conn
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(None)
            s.bind(('localhost', 5555))
            s.listen(1)
            conn, addr = s.accept()
            with conn:
                self.printText("Connected: " + addr[0])
                self.recvMessage()
        except Exception as ex:
            self.printText(ex)

    def connectClient(self, host):

        global conn
        try:
            if host[-6:] == ".onion":
                socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
                conn = socks.socksocket()
                conn.connect((host, 5555))
                self.printText("Connected to: " + host)
                self.recvMessage()
            else:
                conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn.connect((host, 5555))
                self.printText("Connected to: " + host)
                self.recvMessage()
        except Exception as ex:
            self.printText(ex)

    def recvMessage(self):

        while True:
            data = conn.recv(4096)
            if not data: pass
            else: self.printText(data)

    def sendMessage(self, message):

        try:
            if self.enableEncryption:
                conn.send(self.fObj.encrypt(bytes(message, 'utf-8')))
            else:
                conn.send(bytes(message, 'utf-8'))
        except Exception as ex:
            self.printText(ex)

    def printText(self, text):

        if isinstance(text, bytes): #recv messages
            if self.enableEncryption:
                try:
                    ready_text = "[{0}]  {1}".format(datetime.now().strftime("%H:%M:%S"), str(self.fObj.decrypt(text), 'utf-8'))
                except Exception as ex:
                    ready_text = str(ex)
            else:
                ready_text = "[{0}]  {1}".format(datetime.now().strftime("%H:%M:%S"), str(text, 'utf-8'))
        else:
            ready_text = "[{0}]  {1}".format(datetime.now().strftime("%H:%M:%S"), text)
        if self.enableTranslate == True:
            self.list_box_messages.InsertItems([self.tObj.translate(ready_text, dest=language()[0][0:2]).text], 0)
        else:
            self.list_box_messages.InsertItems([ready_text], 0)



    def __set_properties(self):

        self.SetTitle("lucchat")
        self.SetIcon(wx.Icon("img\\icon.ico", wx.BITMAP_TYPE_ICO))
        self.SetBackgroundColour(wx.Colour(98, 98, 98))
        self.SetForegroundColour(wx.Colour(255, 255, 255))
        self.SetFont(wx.Font(9, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Consolas"))
        self.list_box_connection_history.SetMinSize((550, 100))
        self.list_box_connection_history.SetBackgroundColour(wx.Colour(98, 98, 98))
        self.list_box_connection_history.SetForegroundColour(wx.Colour(255, 255, 255))
        self.text_nickname.SetMinSize((150, 25))
        self.bitmap_button_nickname.SetMinSize((100, 25))
        self.bitmap_button_nickname.SetBitmapDisabled(wx.Bitmap("img\\disabledBtn.jpg", wx.BITMAP_TYPE_ANY))
        self.bitmap_button_nickname.SetBitmapPressed(wx.Bitmap("img\\set-nickname-btn-clicked.jpg", wx.BITMAP_TYPE_ANY))
        self.text_host.SetMinSize((340, 25))
        self.bitmap_button_host.SetMinSize((100, 25))
        self.bitmap_button_host.SetBitmapPressed(wx.Bitmap("img\\connect-btn-clicked.jpg", wx.BITMAP_TYPE_ANY))
        self.text_fernet.SetMinSize((340, 25))
        self.bitmap_button_fernet.SetMinSize((100, 25))
        self.bitmap_button_fernet.SetBitmapPressed(wx.Bitmap("img\\message-encryption-btn-clicked.jpg", wx.BITMAP_TYPE_ANY))
        self.list_box_messages.SetMinSize((550, 230))
        self.list_box_messages.SetBackgroundColour(wx.Colour(98, 98, 98))
        self.list_box_messages.SetForegroundColour(wx.Colour(255, 255, 255))
        self.text_send_message.SetMinSize((340, 25))
        self.bitmap_button_send.SetMinSize((100, 25))
        self.bitmap_button_send.SetBitmapPressed(wx.Bitmap("img\\send-btn-clicked.jpg", wx.BITMAP_TYPE_ANY))
        self.bitmap_button_message_encryption.SetMinSize((100, 25))
        self.bitmap_button_message_encryption.SetBitmapPressed(wx.Bitmap("img\\message-translation-btn-clicked.jpg", wx.BITMAP_TYPE_ANY))


    def __do_layout(self):

        grid_sizer_2 = wx.FlexGridSizer(1, 2, 0, 0)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.FlexGridSizer(1, 3, 0, 0)
        sizer_2 = wx.FlexGridSizer(1, 3, 0, 0)
        sizer_5 = wx.FlexGridSizer(1, 3, 0, 0)
        sizer_1.Add(self.list_box_connection_history, 0, wx.BOTTOM | wx.LEFT, 30)
        sizer_5.Add(self.text_nickname, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 30)
        sizer_5.Add((300, 25), 0, wx.ALIGN_BOTTOM, 0)
        sizer_5.Add(self.bitmap_button_nickname, 0, 0, 0)
        sizer_1.Add(sizer_5, 1, wx.EXPAND, 0)
        sizer_2.Add(self.text_host, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 30)
        sizer_2.Add((110, 25), 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_2.Add(self.bitmap_button_host, 0, 0, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        sizer_3.Add(self.text_fernet, 0, wx.LEFT, 30)
        sizer_3.Add((110, 25), 0, 0, 0)
        sizer_3.Add(self.bitmap_button_fernet, 0, 0, 0)
        sizer_1.Add(sizer_3, 1, wx.EXPAND, 0)
        sizer_1.Add(self.list_box_messages, 0, wx.LEFT, 30)
        sizer_4.Add(self.text_send_message, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 30)
        sizer_4.Add(self.bitmap_button_send, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer_4.Add(self.bitmap_button_message_encryption, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer_1.Add(sizer_4, 1, wx.EXPAND, 0)
        grid_sizer_2.Add(sizer_1, 1, wx.EXPAND, 0)
        bitmap_1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("img\\onion.png", wx.BITMAP_TYPE_ANY))
        grid_sizer_2.Add(bitmap_1, 0, 0, 0)
        self.SetSizer(grid_sizer_2)
        self.Layout()
        self.Centre()


    def SetNicknameBtn(self, event):
        self.nickname = self.text_nickname.GetValue()
        self.bitmap_button_nickname.Disable()

    def ConnectBtn(self, event):
        host_connect = self.text_host.GetValue()
        if host_connect == "localhost":
            self.printText("I just started the server on host 127.0.0.1 and port 5555.")
            server = Thread(target=self.runServer)
            server.start()
        else:
            with open("connection-history.log", "a") as w:
                w.write(host_connect + "\n")
                w.close()
            self.list_box_connection_history.InsertItems([host_connect], 0)
            client = Thread(target=self.connectClient, args=(host_connect,))
            client.start()

    def MessageEncryptionBtn(self, event):
        self.enableEncryption = not self.enableEncryption
        if self.fObj == None:
            self.fObj = Fernet(self.text_fernet.GetValue())

    def SendBtn(self, event):
        text = "<{0}> {1}".format(self.nickname, self.text_send_message.GetValue())
        self.printText(text)
        self.sendMessage(text)
        self.text_send_message.Clear()

    def EnableTranslationBtn(self, event):
        self.enableTranslate = not self.enableTranslate
        if self.tObj is None:
            self.tObj = Translator()



class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True



if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
