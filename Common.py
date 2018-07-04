import wx
import os
import re


def save_script(parent, cdlg, file_pre, run_test=False, old_session_name=None):
    pwd_type = cdlg.pwd_type.GetValue()
    session = cdlg.session.GetValue()
    host = cdlg.host.GetValue()
    pwd_detail = cdlg.pwd_key_file_or_password.GetValue()
    user = cdlg.user.GetValue()
    if not host or not pwd_detail or not user or not session:
        dlg = wx.MessageDialog(parent, "请检查……", "主机地址、密码或秘钥文件、登录用户均不能为空", wx.ICON_ERROR)
        dlg.ShowModal()
        cdlg.save_status = False
    else:
        if (pwd_type == "秘钥文件" and (not os.path.isfile(pwd_detail))) or (pwd_type == "文本密码" and os.path.isfile(pwd_detail)):
            dlg = wx.MessageDialog(parent, "请检查……", "密码类型与密码值(文件)不匹配", wx.ICON_ERROR)
            dlg.ShowModal()
            cdlg.save_status = False
        else:
            if old_session_name:
                src = os.path.join(os.getcwd(), "script", old_session_name+".scpt")
                dst = os.path.join(os.getcwd(), "script", file_pre+".scpt")
                print(src, dst)
                os.rename(src, dst)
            else:
                if "%s.scpt" % file_pre in os.listdir("script/") and file_pre != "temp":
                    dlg = wx.MessageDialog(parent, "请检查……", "会话名称已存在，请重新命名", wx.ICON_ERROR)
                    dlg.ShowModal()
                    cdlg.save_status = False
            with open("script/%s.scpt" % file_pre, "w") as f:
                if pwd_type == "秘钥文件":
                    cdlg.temp_script = '''tell application "Terminal"\n\tset currentTab to do script ("ssh -i %s %s@%s")\n\tdelay 3\nend tell''' % (pwd_detail, user, host)
                else:
                    cdlg.temp_script = '''tell application "Terminal"\n\tset currentTab to do script ("ssh %s@%s")\n\tdelay 3\n\tdo script ("%s") in currentTab\nend tell''' % (user, host, pwd_detail)
                f.write(cdlg.temp_script)
                cdlg.save_status = True
            if run_test:
                os.system("osascript script/%s.scpt" % file_pre)


def get_all_session():
    files = os.listdir("script/")
    dic = dict(zip([key.replace(".scpt", "") for key in files if key != "temp.scpt"], [value for value in files if value != "temp.scpt"]))
    return dic


def set_all_session_to_read_only(grid):
    for row in range(grid.GetNumberRows()):
        grid.SetReadOnly(row, 0, isReadOnly=True)


def corners_to_cells(top_lefts, bottom_rights):
    """
    Take lists of top left and bottom right corners, and
    return a list of all the cells in that range
    """
    cells = []
    for top_left, bottom_right in zip(top_lefts, bottom_rights):

        rows_start = top_left[0]
        rows_end = bottom_right[0]

        cols_start = top_left[1]
        cols_end = bottom_right[1]

        rows = range(rows_start, rows_end+1)
        cols = range(cols_start, cols_end+1)

        cells.extend([(row, col) for row in rows for col in cols])

    return cells


def get_selected_cells(grid):
    """
    Return the selected cells in the grid as a list of
    (row, col) pairs.
    We need to take care of three possibilities:
    1. Multiple cells were click-selected (GetSelectedCells)
    2. Multiple cells were drag selected (GetSelectionBlock…)
    3. A single cell only is selected (CursorRow/Col)
    """
    top_left = grid.GetSelectionBlockTopLeft()
    if top_left:
        bottom_right = grid.GetSelectionBlockBottomRight()
        return corners_to_cells(top_left, bottom_right)
    selection = grid.GetSelectedCells()
    if not selection:
        row = grid.GetGridCursorRow()
        col = grid.GetGridCursorCol()
        return [(row, col)]
    return selection


def get_session_json_with_session_name(session_name, session_name_file_dic):
    with open("script/%s" % session_name_file_dic[session_name], "r", encoding="utf-8") as f:
        try:
            data = f.read()
            p_user_host = re.compile(r'\w+@.+"')
            match = p_user_host.search(data)
            user_host = match.group().replace(" ", "").replace("\"", "").split("@")
            user = user_host[0]
            host = user_host[1]
            p_pwd_detail = re.compile(r'ssh -i .+ ')
            match_pwd_detail = p_pwd_detail.search(data)
            if not match_pwd_detail:
                pwd_type = "文本密码"
                p_pwd_detail = re.compile(r'\(".+"\) in')
                match_pwd_detail = p_pwd_detail.search(data)
                pwd_detail = match_pwd_detail.group().replace('") in', '').replace('("', '')
            else:
                pwd_type = "秘钥文件"
                pwd_detail = match_pwd_detail.group().replace("ssh -i", "")
                pwd_detail = pwd_detail.replace(pwd_detail[-1], "")
            info = {"user": user, "host": host, "pwd_type": pwd_type, "pwd_detail": pwd_detail, "session_name": session_name}
            return info
        except:
            return
