#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import wx
import wx.adv
from datetime import datetime
import socks
import socket
import threading
from cryptography.fernet import Fernet
import tor

class MyFrame(wx.Frame):



    def __init__(self, *args, **kwds):

        self.enableEncryption = False
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((800, 556))
        self.text_host = wx.TextCtrl(self, wx.ID_ANY, "localhost")
        self.choice_program = wx.Choice(self, wx.ID_ANY, choices=["server", "client"])
        self.button_program = wx.Button(self, wx.ID_ANY, "Run")
        self.text_fernet = wx.TextCtrl(self, wx.ID_ANY, Fernet.generate_key())
        self.button_fernet = wx.Button(self, wx.ID_ANY, "Decrypt")
        self.list_box_messages = wx.ListBox(self, wx.ID_ANY, choices=[""])
        self.text_send_message = wx.TextCtrl(self, wx.ID_ANY, style=wx.TE_PROCESS_ENTER)
        self.text_send_message.Bind(wx.EVT_TEXT_ENTER, self.buttonSendMessage)
        self.button_send_message = wx.Button(self, wx.ID_ANY, "Send")
        self.hyperlink_github = wx.adv.HyperlinkCtrl(self, wx.ID_ANY, "https://github.com/luccese", "")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.buttonProgramStart, self.button_program)
        self.Bind(wx.EVT_BUTTON, self.buttonFernetEncryption, self.button_fernet)
        self.Bind(wx.EVT_BUTTON, self.buttonSendMessage, self.button_send_message)

    if tor.checkInstall():
        if not(tor.checkRunning()):
            tor.runTor()

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
                conn.send(fObj.encrypt(bytes(message, 'utf-8')))
            else:
                conn.send(bytes(message, 'utf-8'))
        except Exception as ex:
            self.printText(ex)

    def printText(self, text):

        if isinstance(text, bytes):
            if self.enableEncryption:
                try:
                    self.list_box_messages.InsertItems(["[{0}]  {1}".format(datetime.now().strftime("%H:%M:%S"), str(fObj.decrypt(text), 'utf-8'))], 0)
                except Exception as ex:
                    self.printText(ex)
            else:
                self.list_box_messages.InsertItems(["[{0}]  {1}".format(datetime.now().strftime("%H:%M:%S"), str(text, 'utf-8'))], 0)
        else:
            self.list_box_messages.InsertItems(["[{0}]  {1}".format(datetime.now().strftime("%H:%M:%S"), text)], 0)

    def __set_properties(self):

        self.SetTitle("lucchat")
        self.SetBackgroundColour(wx.BLACK)
        self.SetForegroundColour(wx.WHITE)
        self.text_host.SetMinSize((200, 25))
        self.text_host.SetBackgroundColour(wx.BLACK)
        self.text_host.SetForegroundColour(wx.WHITE)
        self.choice_program.SetMinSize((100, 25))
        self.choice_program.SetSelection(0)
        self.button_program.SetMinSize((100, 25))
        self.text_fernet.SetMinSize((350, 25))
        self.text_fernet.SetBackgroundColour(wx.BLACK)
        self.text_fernet.SetForegroundColour(wx.WHITE)
        self.button_fernet.SetMinSize((100, 25))
        self.list_box_messages.SetMinSize((784, 125))
        self.list_box_messages.SetBackgroundColour(wx.BLACK)
        self.list_box_messages.SetForegroundColour(wx.WHITE)
        self.text_send_message.SetMinSize((350, 25))
        self.text_send_message.SetBackgroundColour(wx.BLACK)
        self.text_send_message.SetForegroundColour(wx.WHITE)
        self.button_send_message.SetMinSize((100, 25))

    def __do_layout(self):

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_4 = wx.GridSizer(2, 1, 0, 0)
        grid_sizer_5 = wx.GridSizer(2, 2, 0, 0)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_3 = wx.GridSizer(1, 2, 0, 0)
        grid_sizer_2 = wx.GridSizer(1, 3, 0, 0)
        bitmap_1 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap("logo.jpg", wx.BITMAP_TYPE_ANY))
        sizer_1.Add(bitmap_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_2.Add(self.text_host, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_2.Add(self.choice_program, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_2.Add(self.button_program, 0, wx.ALIGN_CENTER, 0)
        sizer_1.Add(grid_sizer_2, 1, wx.ALL | wx.EXPAND, 0)
        grid_sizer_3.Add(self.text_fernet, 0, wx.ALIGN_CENTER | wx.LEFT, 20)
        grid_sizer_3.Add(self.button_fernet, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.RIGHT, 83)
        sizer_1.Add(grid_sizer_3, 1, wx.EXPAND, 0)
        grid_sizer_4.Add(self.list_box_messages, 0, 0, 0)
        grid_sizer_5.Add(self.text_send_message, 0, wx.ALIGN_CENTER | wx.LEFT, 20)
        grid_sizer_5.Add(self.button_send_message, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.RIGHT, 83)
        label_1 = wx.StaticText(self, wx.ID_ANY, "A:")
        sizer_2.Add(label_1, 0, wx.EXPAND | wx.LEFT, 10)
        label_2 = wx.StaticText(self, wx.ID_ANY, "B:")
        label_2.SetMinSize((36, 16))
        sizer_2.Add(label_2, 0, wx.EXPAND | wx.LEFT, 10)
        label_3 = wx.StaticText(self, wx.ID_ANY, "C:")
        sizer_2.Add(label_3, 0, wx.EXPAND | wx.LEFT, 10)
        grid_sizer_5.Add(sizer_2, 1, wx.EXPAND, 0)
        grid_sizer_5.Add(self.hyperlink_github, 0, wx.ALIGN_CENTER, 0)
        grid_sizer_4.Add(grid_sizer_5, 0, wx.ALL | wx.EXPAND, 0)
        sizer_1.Add(grid_sizer_4, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        self.Layout()

    def buttonProgramStart(self, event):

        if self.choice_program.GetSelection() == 0:
            self.printText("I just started the server on host 127.0.0.1 and port 5555.")
            server = threading.Thread(target=self.runServer)
            server.start()
        else:
            client = threading.Thread(target=self.connectClient, args=(self.text_host.GetValue(),))
            client.start()

    def buttonFernetEncryption(self, event):

        global fObj
        fKey = self.text_fernet.GetValue()
        self.enableEncryption = True
        fObj = Fernet(fKey)

    def buttonSendMessage(self, event):

        text = self.text_send_message.GetValue()
        self.printText(text)
        self.sendMessage(text)
        self.text_send_message.Clear()

class MyApp(wx.App):

    def OnInit(self):

        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
