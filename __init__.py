from distutils.spawn import find_executable
import tempfile
import subprocess
import sys

import aqt
from aqt import mw

BUILTIN_EDITOR = aqt.editor.Editor._onHtmlEdit


def get_editor():
    config = mw.addonManager.getConfig(__name__)
    user_choice = config.get("editor")
    editors = [
        user_choice,
        user_choice + ".exe",
        "notepad++.exe",
        "notepad.exe",
        "gvim -f",
        "vim -gf",
        "atom",
        "atom.exe",
        "gedit",
    ]
    if sys.platform == "darwin":
        editors.append("open -t")
    for editor in editors:
        command = editor.split()
        executable = find_executable(command[0])
        if executable:
            command[0] = executable
            return " ".join(command)

    raise RuntimeError("Could not find external editor")


def edit(text):
    editor = get_editor()
    filename = tempfile.mktemp(suffix=".html")

    with open(filename, "wt", encoding="utf-8") as file:
        file.write(text)

    cmd_list = editor.split() + [filename]
    proc = subprocess.Popen(cmd_list, close_fds=True)
    proc.communicate()

    with open(filename, "rt", encoding="utf-8") as file:
        return file.read()


def edit_with_external_editor(self, field):
    text = self.note.fields[field]
    try:
        text = edit(text)
        self.note.fields[field] = text
        self.note.flush()
        self.loadNote(focusTo=field)
    except RuntimeError:
        return BUILTIN_EDITOR(self, field)


aqt.editor.Editor._onHtmlEdit = edit_with_external_editor
