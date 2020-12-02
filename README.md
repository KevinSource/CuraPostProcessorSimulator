# Ultimaker Cura Simulator

Use this file set to test post-processors for Ultimaker Cura
There are three elementary Python modules needed to simplify testing Cura post-processing extension modules. This enables the use of your favorite integrated development environment (IDE) for debugging. The folder needs to have these modules: 

1. getSettingDataSimulator.py - This module reads string you are developing to input your post-processor's parameters in the getSettingDataString method. It uses tkinter to display the parameters for testing. The parameters are saved to make iterative testing easier. This module does NOT do drop down selection for enum variables, nor does it select related variables based on enum selections. Could be done but didn’t seem necessary for the purposes of testing post-processing logic.

2. BuildLayerList.py – This reads a gcode file and creates a Python list with a layer per entry. This is what Ultimaker Cura passes to post-processing extension modules.

3. findfqpath.py – This is a convenience module. It finds the path for the cura.log file. That path is used to build an xcopy batch file in the current folder to copy the module being developed from the development folder to the Ultimaker Cura scripts folder. The first time this runs, it will take a minute or two. After that, it will run sub-second. (Also available with: pip install findfqpath) 

FOUR  MODIFICATIONS ARE REQUIRED TO THE POST-PROCESSING MODULE ITSELF. These changes can be left and will not affect the module execution when the module is executed in the Ultimaker Cura application.

********************************** 1 ***************************************
********************************** 1 ***************************************
********************************** 1 ***************************************
Replace:     from ..Script import Script # When called from Cura
With:
if __name__ == '__main__':
    import getSettingDataSimulator
    import os
    from findfqpath import find_fq_path
else:
    from ..Script import Script # When called from Cura

********************************** 2 ***************************************
********************************** 2 ***************************************
********************************** 2 ***************************************
Replace: class YourPostProcessModuleName(Script):
With:
if __name__ == '__main__':
    ClassNm = getSettingDataSimulator.ScriptSim
else:
    ClassNm = Script

class YourPostProcessModuleName (ClassNm):

********************************** 3 ***************************************
********************************** 3 ***************************************
********************************** 3 ***************************************
Replace: 
def execute(self,data):
    if __name__ == '__main__':
        UseModule = getSettingDataSimulator.ScriptSim
    else:
        UseModule = self

    Parameter_1 = UseModule.getSettingValueByKey("Parameter_1")
    Parameter_2 = UseModule.getSettingValueByKey("Parameter_2")

********************************** 4 ***************************************
********************************** 4 ***************************************
********************************** 4 ***************************************
# ***************************************************************************
# * This code only executes while debugging for now.
# * When called by Cura, the __name__ is not __main__, so this doesn't run
# * Put the code to execute your post-processor here
# ***************************************************************************

if __name__ == '__main__':
    from BuildLayerList import BuildLayerList

    #************************************************************************
    # * Put the input and output files here
    # * Generate and save a gcode file from Ultimaker Cura - Use that as the                        
    # * input file
    # * Give the after file a different name
    #************************************************************************    FileIn = r"C:\Users\YourPath\CE3_20mm_calibration_cube_Before.gcode"
    FileOUt = r"C:\Users\YourPath\CE3_20mm_calibration_cube_After.gcode"

    #**************************************************************************
    # * This uses the parameter settings list to enable user input
    # * The simulator is not as sophisticated as Ultimaker Cura, but it should be 
    # * OK for testing
    # * It uses tkinter
    # **************************************************************************    FileNm = os.path.basename(__file__).split(".")[0]
    ppMod = eval(FileNm)()
    setting_data_as_string = ppMod.getSettingDataString()

    getSettingDataSimulator.ScriptSim.getPostProcessParameters(setting_data_as_string)

    #**********************************************************************
    #* Parses a Gcode file into a list by layer to pass to the Cura 
    # * post-processor extension
    # * just like Ultimaker Cura passes the information
    #************************************************************************
    LayerList = BuildLayerList(FileIn)

    # ***********************************************************************
    # * Calls the execute method just like Ultimaker Cura does
    # * Test away my friend
    # ******************************************************************
    NewList1 = ppMod.execute(LayerList)  
    # **********************************************************************
    # * Writes the results for your review
    # ***********************************************************************
    with open(FileOUt, "w") as File_Out:
        for line in NewList1:
            File_Out.write(line)
            File_Out.write("\n")

    # **************************************************************************
    # * Writes a .bat file to copy this module to the Cura script folder
    # * The first tile this runs, it can take a minute or two. After that, it
    # * will run sub-second
    # **************************************************************************
    CuraLogPath = find_fq_path("Cura.log", 7, scope="Local")
    CuraScriptPath = os.path.dirname(CuraLogPath) + r"\scripts"
    script_path = os.path.realpath(__file__)
    xCopyBatPath = os.path.dirname(os.path.realpath(__file__)) + r"\CopyToCura.bat"
    xcopyCmd = "xcopy " + '"' + script_path + '"' + " " + '"' + CuraScriptPath + '" /y'
    
    with open(xCopyBatPath, "w") as Bat_Out:
        Bat_Out.write(xcopyCmd)
        Bat_Out.write("\npause")
        Bat_Out.write("\n")

*************************************************************************
*************************************************************************
*************************************************************************

Sample Applications:
CuraGcodeatLayer.py
FilamentChange.py
