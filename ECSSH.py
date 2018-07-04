import wx.grid
from CustomDialog import CreateSessionDialog
from Common import *


class SSH(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="ECSSH", pos=wx.DefaultPosition, size=wx.Size(650, 480), style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)
        self.panel = wx.Panel(self, -1)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_top = wx.GridSizer(1, 4, 5, 5)
        btn_add = wx.Button(self.panel, -1, "打开")
        btn_add.Bind(wx.EVT_BUTTON, self.open_session_by_button)
        btn_new = wx.Button(self.panel, -1, "新建")
        btn_new.Bind(wx.EVT_BUTTON, self.on_click_new_session)
        btn_modify = wx.Button(self.panel, -1, "修改")
        btn_modify.Bind(wx.EVT_BUTTON, self.edit_session_by_button)
        btn_del = wx.Button(self.panel, -1, "删除")
        btn_del.Bind(wx.EVT_BUTTON, self.del_session_by_button)

        sizer_top.Add(btn_add, 0, wx.EXPAND)
        sizer_top.Add(btn_new, 0, wx.EXPAND)
        sizer_top.Add(btn_modify, 0, wx.EXPAND)
        sizer_top.Add(btn_del, 0, wx.EXPAND)

        self.sessions = wx.grid.Grid(self.panel, -1)
        self.sessions_dict = get_all_session()
        self.sessions.CreateGrid(len(self.sessions_dict), 1)
        set_all_session_to_read_only(self.sessions)
        self.set_sessions()
        self.sessions.SetRowLabelSize(0)
        self.sessions.SetColLabelValue(0, "会话列表")
        self.sessions.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)
        self.sessions.EnableDragColMove(False)
        self.sessions.EnableDragColSize(True)
        self.sessions.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.sessions.EnableDragRowSize(True)
        self.sessions.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.sessions.Bind(wx.EVT_SIZE, self.on_size)
        self.sessions.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.open_session)
        self.sessions.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_show_pop_up)
        self.sessions.GetGridWindow().Bind(wx.EVT_RIGHT_DOWN, self.on_show_pop_up)
        self.sessions.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_single_select)
        self.sizer.Add(sizer_top, flag=wx.EXPAND | wx.ALL, border=5)
        self.sizer.Add(self.sessions, 1, flag=wx.EXPAND, border=10)
        self.panel.Bind(wx.EVT_CONTEXT_MENU, self.on_show_pop_up)
        self.panel.SetSizer(self.sizer)
        self.Layout()
        self.Centre(wx.BOTH)
        self.Show()
        self.operation_index = (0, 0)
        self.operation_session_name = list(self.sessions_dict.keys())[0]
        self.currentlySelectedCell = (0, 0)

    def del_session_by_button(self, evt):
        dlg = wx.MessageDialog(self, "确定删除吗？", "⚠️会话删除将不可恢复⚠️", wx.OK | wx.CANCEL)
        result = dlg.ShowModal()
        if result == wx.ID_OK:
            os.remove(os.path.abspath("script/%s" % self.sessions_dict[self.operation_session_name]))
            self.sessions.DeleteRows(self.operation_index[0])
            self.Layout()
        dlg.Destroy()

    def edit_session_by_button(self, evt):
        session_name = self.sessions.GetCellValue(self.currentlySelectedCell[0], self.currentlySelectedCell[1])
        session_json = get_session_json_with_session_name(session_name, self.sessions_dict)
        if session_json:
            create_dialog = CreateSessionDialog(parent=self, host=session_json["host"], user=session_json["user"], pwd_detail=session_json["pwd_detail"], pwd_type=session_json["pwd_type"],
                                                session_name=session_json["session_name"])
            result = create_dialog.ShowModal()
            if result == wx.ID_OK:
                self.save_session(cdlg=create_dialog, pattern="replace")
            create_dialog.Destroy()
        else:
            dlg = wx.MessageDialog(self, "Shit!", "会话解析失败", wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def on_single_select(self, evt):
        self.currentlySelectedCell = evt.GetRow(), evt.GetCol()
        self.operation_session_name = self.sessions.GetCellValue(self.currentlySelectedCell[0], self.currentlySelectedCell[1])
        self.operation_index = self.currentlySelectedCell[0], self.currentlySelectedCell[1]
        evt.Skip()

    def open_session_by_button(self, evt):
        session_name = self.sessions.GetCellValue(self.currentlySelectedCell[0], self.currentlySelectedCell[1])
        print(session_name, self.sessions_dict)
        os.system("osascript script/%s" % (self.sessions_dict[session_name]))

    def on_popup_item_selected(self, evt):
        item = self.popup_menu.FindItemById(evt.GetId())
        operation = item.GetText()
        self.operation_on_right_click(operation)

    def operation_on_right_click(self, operation):
        self.operation_session_name = self.sessions.GetCellValue(self.operation_index[0], self.operation_index[1])
        if operation == "修改":
            session_json = get_session_json_with_session_name(self.operation_session_name, self.sessions_dict)
            if session_json:
                create_dialog = CreateSessionDialog(parent=self, host=session_json["host"], user=session_json["user"], pwd_detail=session_json["pwd_detail"], pwd_type=session_json["pwd_type"],
                                                    session_name=session_json["session_name"])
                result = create_dialog.ShowModal()
                if result == wx.ID_OK:
                    self.save_session(cdlg=create_dialog, pattern="replace")
                create_dialog.Destroy()
            else:
                dlg = wx.MessageDialog(self, "Shit!", "会话解析失败", wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
        elif operation == "连接":
            os.system("osascript script/%s" % (self.sessions_dict[self.operation_session_name]))
        else:
            dlg = wx.MessageDialog(self, "确定删除吗？", "⚠️会话删除将不可恢复⚠️", wx.OK | wx.CANCEL)
            result = dlg.ShowModal()
            if result == wx.ID_OK:
                os.remove(os.path.abspath("script/%s" % self.sessions_dict[self.operation_session_name]))
                self.sessions.DeleteRows(self.operation_index[0])
                self.Layout()
            dlg.Destroy()

    def on_show_pop_up(self, evt):
        x, y = self.sessions.CalcUnscrolledPosition(evt.GetX(), evt.GetY())
        self.operation_index = self.sessions.XYToCell(x, y)
        self.popup_menu = wx.Menu()
        self.popup_menu.Bind(wx.EVT_MENU, self.on_popup_item_selected)
        if not hasattr(self, "popup_ID_modify"):
            self.popup_ID_modify = wx.NewId()
            self.popup_ID_connect = wx.NewId()
            self.popup_ID_delete = wx.NewId()
        self.item_modify = wx.MenuItem(self.popup_menu, self.popup_ID_modify, "修改")
        self.popup_menu.Append(self.item_modify)
        self.popup_menu.Append(self.popup_ID_connect, "连接")
        self.popup_menu.Append(self.popup_ID_delete, "删除")
        self.PopupMenu(self.popup_menu)
        self.popup_menu.Destroy()

    def set_sessions(self):
        counter = 0
        for name in self.sessions_dict.keys():
            self.sessions.SetCellValue(counter, 0, name)
            counter += 1

    def save_session(self, cdlg, pattern="create"):
        session = cdlg.session.GetValue()
        if pattern != "create":
            save_script(parent=self, cdlg=cdlg, file_pre=session, run_test=False, old_session_name=self.operation_session_name)
        else:
            save_script(parent=self, cdlg=cdlg, file_pre=session, run_test=False)
        if cdlg.save_status:
            pre_keys = list(self.sessions_dict.keys())
            self.sessions_dict = get_all_session()
            now_keys = list(self.sessions_dict.keys())
            print(self.sessions_dict)
            dlg = wx.MessageDialog(parent=self, message="SUCCESS", caption="保存成功！", style=wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            if pattern == "create":
                self.sessions.AppendRows()
                self.sessions.SetCellValue(self.sessions.GetNumberRows()-1, 0, [name for name in now_keys if name not in pre_keys][0])
            else:
                print(self.operation_index[0], self.operation_index[1])
                self.sessions.SetCellValue(self.operation_index[0], self.operation_index[1], session)
            set_all_session_to_read_only(self.sessions)
            self.Layout()

    def on_click_new_session(self, evt):
        create_dialog = CreateSessionDialog(parent=self)
        result = create_dialog.ShowModal()
        if result == wx.ID_OK:
            self.save_session(cdlg=create_dialog)
        create_dialog.Destroy()

    def open_session(self, evt):
        row = evt.GetRow()
        session_name = self.sessions.GetCellValue(row, 0)
        print(session_name, self.sessions_dict)
        os.system("osascript script/%s" % (self.sessions_dict[session_name]))

    def on_size(self, evt):
        width, height = self.GetSize()
        for col in range(1):
            self.sessions.SetColSize(col, width*0.95)

    def show_menu(self, evt):
        print(get_selected_cells(self.sessions))


if __name__ == "__main__":
    app = wx.App()
    SSH(None)
    app.MainLoop()
