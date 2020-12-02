#! python3
# Copyright (c) 2017 Ruben Dulek
# The PostProcessingPlugin is released under the terms of the AGPLv3 or higher.
# *****************************************************************************************************
# This if statement brings in the right imports in both Cura and test
# *****************************************************************************************************
if __name__ == '__main__':
    import getSettingDataSimulator
    import os
    from findfqpath import find_fq_path
else:
    from ..Script import Script # When called from Cura


# *****************************************************************************************************
# This if statement sets the class to Script in Cura, but to the test class ScriptSim in test
# *****************************************************************************************************
if __name__ == '__main__':
    ClassNm = getSettingDataSimulator.ScriptSim
else:
    ClassNm = Script

class CuraGcodeatLayer(ClassNm):

    # *****************************************************************************************************
    # Set up paramter input string
    # *****************************************************************************************************

    def getSettingDataString(self):
        return """{
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

    def execute(self,data):
        # *****************************************************************************************************
        # Get the parameters entered by the user
        # *****************************************************************************************************
        if __name__ == '__main__':
            UseModule = getSettingDataSimulator.ScriptSim
        else:
            UseModule = self

        Target_Layer_Num = UseModule.getSettingValueByKey("Layer")
        Gcode_In = UseModule.getSettingValueByKey("GCode")
        # *****************************************************************************************************
        # The next lines will replace the \n literal with actual line feeds
        # *****************************************************************************************************
        Gcode_In=Gcode_In.strip()
        NewGcode_In = Gcode_In.replace(r"\n", "\n")

        # *****************************************************************************************************
        # The following code loop gets rid of the extra spaces that were in the input string
        # *****************************************************************************************************
        GcodeList = NewGcode_In.split("\n")
        CleanGcodeStr = ""
        for line in GcodeList:
            CleanGcodeStr += line.lstrip() + "\n"
        CleanGcodeStr = CleanGcodeStr[:-1]

        # *****************************************************************************************************
        # Thge following code formats the input string for use in the printer
        # *****************************************************************************************************
        GCode_str =  ";[CAZD:\n" + CleanGcodeStr + "\n;:CAZD]"

        # ********************************************************************************************************
        # * Loop through the layers of the data until you get to the layer specified
        # ********************************************************************************************************
        # *****************************************************************************************************
        # Put the gcode modification instructions here
        # *****************************************************************************************************

        data_out=[]
        for layer_number, layer in enumerate(data):
            try:
                AfterColon = layer.split(':', 1)[1]  # Gets everything after the :
                if layer[1:7] == 'LAYER:':
                    LayerNum = int(AfterColon.split("\n", 1)[0])  # Gets the Layer number
                else:
                    LayerNum = -1
            except:
                LayerNum = -1

            if Target_Layer_Num == LayerNum:
                newstr = layer.split("\n", 1)[0] + '\n' + GCode_str  + '\n' + layer.split("\n", 1)[1]
                data_out.append(newstr)
            else:
                data_out.append(layer)

        return data_out


# ********************************************************************************************************
# * This code only executes while debugging for now.
# * When called by Cura, the __name__ is not __main__, so this doesn't run
# ********************************************************************************************************
if __name__ == '__main__':
    from BuildLayerList import BuildLayerList

    # ********************************************************************************************************
    # * Put the input and output files here
    # * Generate and save a gcode file from Ultimaker Cura - Use that as the input file
    # * Give the after file a different name
    # ********************************************************************************************************
    FileIn = r"C:\Users\Public\Documents\Python\CuraPostProcessSimulator\CE3_20mm_calibration_cube_Before.gcode"
    FileOUt = r"C:\Users\Public\Documents\Python\CuraPostProcessSimulator\CE3_20mm_calibration_cube_After.gcode"

    # ********************************************************************************************************
    # * This uses the parameter settings list to enable user input
    # * The simulator is not as sophisticated as Ultimaker Cura, but it should be OK for testing
    # * It uses tkinter
    # ********************************************************************************************************
    FileNm = os.path.basename(__file__).split(".")[0]
    ppMod = eval(FileNm)()
    setting_data_as_string = ppMod.getSettingDataString()
    getSettingDataSimulator.ScriptSim.getPostProcessParameters(setting_data_as_string)

    # ********************************************************************************************************
    # * Parses a Gcode file into a list by layer to pass to the Cura post-processor extension
    # * just like Ultimaker Cura passes the information
    # ********************************************************************************************************
    LayerList = BuildLayerList(FileIn)

    # ********************************************************************************************************
    # * Calls the execute method just like Ultimaker Cura does
    # * Test away my friend
    # ********************************************************************************************************
    NewList1 = ppMod.execute(LayerList)  # CuraGcodeatLayer.execute

    # ********************************************************************************************************
    # * Writes the results for your review
    # ********************************************************************************************************
    with open(FileOUt, "w") as File_Out:
        for line in NewList1:
            File_Out.write(line)
            File_Out.write("\n")

    # ********************************************************************************************************
    # * Writes a .bat file to copy this module to the cura script folder
    # * The first tile this runs, it can take a minute or two. After that, it will run sub-second
    # ********************************************************************************************************
    CuraLogPath = find_fq_path("Cura.log", 7, scope="Local")
    CuraScriptPath = os.path.dirname(CuraLogPath) + r"\scripts"
    script_path = os.path.realpath(__file__)
    xCopyBatPath = os.path.dirname(os.path.realpath(__file__)) + r"\CopyToCura.bat"
    xcopyCmd = "xcopy " + '"' + script_path + '"' + " " + '"' + CuraScriptPath + '" /y'

    with open(xCopyBatPath, "w") as Bat_Out:
        Bat_Out.write(xcopyCmd)
        Bat_Out.write("\npause")
        Bat_Out.write("\n")

    x = 1