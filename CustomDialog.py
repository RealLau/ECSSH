import wx
from Common import save_script


class CreateSessionDialog(wx.Dialog):
    def __init__(self, parent, host="", pwd_type="文本密码", pwd_detail="", session_name="", user=""):
        wx.Dialog.__init__(self, parent, -1, '创建会话', size=(250, 400))
        self.Centre()
        self.session_name_text = wx.StaticText(self, -1, "会话别名: ", pos=(10, 15))
        self.session = wx.TextCtrl(self, pos=(85, 15), size=(150, 20), value=session_name)

        self.host_text = wx.StaticText(self, -1, "主机地址: ", pos=(10, 60))
        self.host = wx.TextCtrl(self, pos=(85, 60), size=(150, 20), value=host)
        self.pwd_type_text = wx.StaticText(self, -1, "密码类型: ", pos=(10, 105))
        self.pwd_type = wx.ComboBox(self, -1, choices=["文本密码", "秘钥文件"], pos=(85, 105), size=(150, 30), style=wx.CB_READONLY)

        self.pwd_type.SetValue(pwd_type)
        self.pwd_type.Bind(wx.EVT_COMBOBOX, self.on_select_pwd_type)
        self.pwd_type_value = None
        self.pwd_key_file_or_password_text = wx.StaticText(self, -1, "密码或秘钥文件: ", pos=(10, 160))
        self.pwd_key_file_or_password = wx.TextCtrl(self, -1, pos=(120, 160), size=(115, 20), value=pwd_detail)
        self.user_text = wx.StaticText(self, -1, "登录用户: ", pos=(10, 205))
        self.user = wx.TextCtrl(self, pos=(85, 205), size=(150, 20), value=user)
        self.divide_line = wx.StaticLine(self, -1, pos=(10, 275), size=(230, 2))
        wx.Button(self, wx.ID_CANCEL, "取消", pos=(5, 320), size=(80, 20))
        self.test = wx.Button(self, wx.ID_ANY, "测试连接", pos=(85, 320), size=(80, 20))
        self.test.Bind(wx.EVT_BUTTON, self.test_connection)
        self.save_button = wx.Button(self, wx.ID_OK, "确定", pos=(165, 320), size=(80, 20))
        self.temp_script = None
        self.save_status = False

    def on_select_pwd_type(self, evt):
        self.pwd_type_value = evt.GetString()
        if self.pwd_type_value == "秘钥文件":
            with wx.FileDialog(self, "秘钥文件", wildcard="KEY files (*.key)|*.key", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return
                pathname = fileDialog.GetPath()
                self.pwd_key_file_or_password.SetValue(pathname)

    def test_connection(self, evt):
        save_script(parent=self, cdlg=self, file_pre="temp", run_test=True)

