#! python3
# Copyright (c) 2020 Kevin Doglio, Orlando Fl
# The Module is released under the terms of the AGPLv3 or higher.
# ********************************************************************************************************
# * Simulates Ultimaker Cura to get user input
# ********************************************************************************************************
import inspect
import logging
import os
import tkinter as tk
from tkinter import *
from tkinter import ttk
from typing import Union
import json
import collections

# ********************************************************************************************************
# * This class handles the data conversion from string to int, float, bool etc
# * Would use a select/case statement in any other language
# ********************************************************************************************************
class varTypeSw:

    def Switch(self,Type, strValue, Default, Options):
        default = strValue
        switchName = "case_" + Type
        outVar = getattr(self, switchName,lambda:default)(strValue,Default,Options)
        return outVar

    def case_str(self,strValue,Default,Options):
            if strValue.strip() == "":
                return Default
            else:
                return strValue

    def case_int(self,strValue,Default,Options):
            try:
                int_out = int(strValue)
            except ValueError:
                try:
                    int_out = int(Default)
                except ValueError:
                    int_out = 0
            return int_out

    def case_float(self,strValue,Default,Options):
            try:
                float_out = float(strValue)
            except ValueError:
                try:
                    float_out = float(Default)
                except ValueError:
                    float_out = 0
            return float_out

    def case_enum(self,strValue,Default,Options):
            try:
                dict_out = Options
            except:
                dict_out = {}
            return dict_out

    def case_bool(self,strValue,Default,Options):
            return Default

class ScriptSim:
    # ********************************************************************************************************
    # * This is the main window for entering the post processor information
    # ********************************************************************************************************
    class SettingsDialog(tk.Frame):
        def __init__(self, parent,setting_data):
            tk.Frame.__init__(self, parent)
            global data_flds
            global data_labels
            global entry_fld_row_start
            global entry_fld_col_start
            global g_row, g_col
            global data_flds_changed
            global label_flds_changed
            global lb_frame
            global dialog_title
            global parmFileName
            global parmPath
            global postProcessData
            global sd
            global root_logger
            # ********************************************************************************************************
            # * Set up logging
            # * To turn on logging, set root_logger.disabled = False
            # * To turn off logging, set root_logger.disabled = True
            # ********************************************************************************************************
            root_logger = logging.getLogger()
            root_logger.disabled = True  # Set to false to see debugging info
            logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

            file_name = ""
            if root_logger.disabled == False:
                file_name = inspect.stack()[0][3]  # This is slow, so only run it when logging
                called_from = lambda n=1: sys._getframe(n + 1).f_code.co_name
                logging.debug('Start of ' + file_name + ' function' + " Called from: " + called_from.__module__)

            sd=setting_data
            postProcessData = {}
            dialog_title = "Post-process Simulator Parameters"

            data_flds_changed = False
            label_flds_changed = False

            # ********************************************************************************************************
            # * Give this window the focus
            # ********************************************************************************************************
            parent.iconify()
            parent.update()
            parent.deiconify()

            # ********************************************************************************************************
            # * Bind the enter key to the OK button
            # * Bind the escape key to the Cancel button
            # ********************************************************************************************************
            parent.bind('<Return>', self.return_ok)
            parent.bind('<Escape>', self.return_cancel)

            g_row = 0
            g_col = 0
            lb_frame = Frame(parent, height=300, width=300, bd=1, relief=SUNKEN)
            lb_frame.grid(row=g_row,column=g_col, sticky=W, padx=5, pady=15)

            # ********************************************************************************************************
            # * Insert the data entry fields
            # ********************************************************************************************************
            self.usr_data = tk.Entry(lb_frame)
            i = 0
            entry_fld_row_start = g_row
            entry_fld_col_start = g_col
            g_col = 1
            g_row += 1
            data_labels = []
            data_flds = []
            self.load_entry_flds(setting_data,entry_fld_row_start,entry_fld_col_start)

            # ********************************************************************************************************
            # * Put a separator line. Not sure this actually does anything.
            # ********************************************************************************************************
            g_row += 1
            rowspan = 4
            separator1 = ttk.Separator(self)
            separator1.grid(row=g_row, column=g_col, padx=5, pady=5, columnspan=4, rowspan=rowspan, sticky="EW")

            # ********************************************************************************************************
            # * Paint "OK", "Cancel" buttons on the dialog
            # ********************************************************************************************************
            g_row += 2
            self.ok_button = Button(parent, text='OK', command=self.return_ok)
            self.ok_button.grid(row=g_row, column=0, sticky=W + E, pady=4, padx=100)
            self.return_button = Button(parent, text='Cancel', command=self.return_cancel)
            self.return_button.grid(row=g_row, column=1, sticky=W + E, pady=4, padx=20)

        # ********************************************************************************************************
        # * Destroy the dialog. Call the routine to update the data.
        # ********************************************************************************************************
        def return_ok(self,event=None):
            # ********************************************************************************************************
            # * Need event=None because clicking the button does not send a parm, but return key does
            # ********************************************************************************************************
            logging.debug('return_ok: Button Click')

            self.write_data_if_needed('return_ok')
            self.master.destroy()

            return postProcessData

        # ********************************************************************************************************
        # * Write the parameter info to a file
        # ********************************************************************************************************
        def write_data_if_needed(self, called_from):
            global parm_list

            logging.debug('write_data_if_needed: ' + called_from)

            if data_flds_changed is True:

                # ********************************************************************************************************
                # * Put the user data in a dictionary
                # ********************************************************************************************************
                postProcessData.clear()
                s = varTypeSw()

                for i in range(len(data_labels)):
                    for entry1 in sd["settings"]:
                        if sd["settings"][entry1]["label"] == data_labels[i]["text"]:
                            EntryIndx = entry1
                            break

                    entryValue = s.Switch(sd["settings"][EntryIndx].get("type"),
                                          data_flds[i].get(),
                                          sd["settings"][EntryIndx].get("default_value", " "),
                                          sd["settings"][EntryIndx].get("options", ""))
                    postProcessData.update({EntryIndx: entryValue})

                logging.debug('postProcessData after: %s', list(postProcessData))

                # ********************************************************************************************************
                # * Delete the original user data
                # ********************************************************************************************************
                logging.debug('Parm File Name: ' + parmPath)
                try:
                    os.remove(parmPath)
                except OSError:
                    pass

                # ********************************************************************************************************
                # * Write the parm data
                # ********************************************************************************************************
                with open(parmPath, 'w') as f:
                    f.write(json.dumps(postProcessData)) # use `json.loads` to do the reverse

        # ********************************************************************************************************
        # * Done. Leave
        # ********************************************************************************************************
        def return_cancel(self, event=None):
            # ********************************************************************************************************
            # * Need event=None because clicking the button does not send a parm, but escape key does
            # ********************************************************************************************************

            logging.debug('return_cancel: Button Click')
            self.master.destroy()

        # ********************************************************************************************************
        # * This triggers if anything changes in the data fields. It sets a flag and updates the OK button text
        # ********************************************************************************************************
        def EntryFld_KeyPressEvent(self,event):
            global data_flds_changed
            global ok_button
            logging.debug('EntryFld_KeyPressEvent: Entry Field Changed')
            data_flds_changed = True
            self.ok_button["text"] = "Update"

        # # ********************************************************************************************************
        # # * This triggers if anything changes in the label fields. It sets a flag and updates the OK button text
        # # ********************************************************************************************************
        # def LabelFld_KeyPressEvent(self,event):
        #     global label_flds_changed
        #     logging.debug('EntryFld_KeyPressEvent: Label Field Changed')
        #     label_flds_changed = True
        #     self.ok_button["text"] = "Update"

        # ********************************************************************************************************
        # * This loads the data and label fields from the settings data
        # ********************************************************************************************************
        def load_entry_flds(self,setting_data,entry_fld_row_start,entry_fld_col_start):
            g_row = entry_fld_row_start
            g_col = entry_fld_col_start
            pady = 2

            s = varTypeSw()

            logging.debug('setting_data: ')
            logging.debug(setting_data)
            fld = 0
            for dtaEntry in setting_data["settings"]:
                data_labels.append(Label(lb_frame,text=setting_data["settings"][dtaEntry]["label"]))
                v_name = "data_flds" + str(fld)
                data_flds.append(Entry(lb_frame))

                data_labels[fld].grid(row=g_row, column=g_col, sticky=W, padx=5, pady=pady)

                data_flds[fld].bind("<Key>", self.EntryFld_KeyPressEvent)  #  shorthand for <ButtonPress-1>
                defaultIt = setting_data["settings"][dtaEntry].get("default_value"," ")
                data_flds[fld].insert(fld, parm_list.get(setting_data["settings"][dtaEntry]["label"],defaultIt))

                data_flds[fld].grid(row=g_row, column=g_col + 1, sticky=W, padx=5, pady=pady)

                entryValue = s.Switch(sd["settings"][dtaEntry]["type"],
                                      data_flds[fld].get(),
                                      setting_data["settings"][dtaEntry].get("default_value"," "),
                                      setting_data["settings"][dtaEntry].get("options",""))
                postProcessData.update({dtaEntry: entryValue})

                g_row += 1
                fld += 1

    # ********************************************************************************************************
    # * Reads the settings data if there is any
    # ********************************************************************************************************
    def read_parm_info(self):
        global parm_list
        global default_user_data
        global parmPath
        global rebate_data_fields_and_values_file

        # ********************************************************************************************************
        # * This figures out where the script is stored
        # ********************************************************************************************************
        script_path: Union[bytes, str] = os.path.dirname(os.path.realpath(sys.argv[0]))
        # logging.debug('Script Directory:' + script_path)

        parmFileName = r'\SavePostProcessParms.txt'
        parmPath = os.path.dirname(os.path.realpath(sys.argv[0]))
        parmPath = parmPath + parmFileName
        # logging.debug('SavePostProcessParms Path and File:' + parmPath)

        if os.path.exists(parmPath):
            with open(parmPath) as f:
                parm_list = json.loads(f.read())
        else:
            parm_list = {"NoData": "NoData"}

        if len(parm_list)==0:
            parm_list = {"NoData": "NoData"}

    # ********************************************************************************************************
    # * This drives the dialog
    # ********************************************************************************************************
    def getPostProcessParameters(setting_data_as_string):

        ParmClass = ScriptSim()

        ParmClass.read_parm_info()
        setting_data = json.loads(setting_data_as_string, object_pairs_hook=collections.OrderedDict)


        settings_root = tk.Tk()
        s_diag = ParmClass.SettingsDialog(settings_root,setting_data)
        settings_root.title(dialog_title)
        settings_root.wait_window(settings_root)

    # ********************************************************************************************************
    # * Simulates Ultimaker Cura to return user data
    # ********************************************************************************************************
    def getSettingValueByKey(key):
        return postProcessData.get(key)



# ********************************************************************************************************
# * test stuff for unit testing this module
# ********************************************************************************************************
if __name__ == "__main__":
    ParmClass = ScriptSim()

    ParmClass.read_parm_info()

    setting_data_as_string = """{
            "name": "Insert Gcode at Layer",
            "key": "CuraGcodeatLayer",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "Layer":
                {
                    "label": "Layer",
                    "description": "Insert Gcode first thing in a layer",
                    "type": "int",
                    "default_value": 0
                },
                "GCode":
                {
                    "label": "GCode",
                    "description": "The GCode to be inserted",
                    "type": "str",
                    "default_value": ""
                }
            }
        }"""

    global setting_data
    setting_data = json.loads(setting_data_as_string, object_pairs_hook=collections.OrderedDict)

    Settings_root = tk.Tk()
    s_diag = ParmClass.SettingsDialog(Settings_root,setting_data)
    Settings_root.title(dialog_title)
    Settings_root.mainloop()
