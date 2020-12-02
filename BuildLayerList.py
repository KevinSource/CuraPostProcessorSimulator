#! python3
# Copyright (c) 2020 Kevin Doglio, Orlando Fl
# The Module is released under the terms of the AGPLv3 or higher.

def BuildLayerList(FileNameIn) -> list([str]):
    FileIn = FileNameIn

    # Read the gcode file into a list of lines, strip off the newline character
    with open(FileIn) as File_In:
        Lines = [line.rstrip() for line in File_In]

    # Reformat into a list of layers
    LayerList = []
    ListCntr = 0
    LayerStr = ""
    for line in Lines:
        if ';LAYER:' in line:
            LayerList.append(LayerStr[:-1])
            LayerStr = ""
            ListCntr = + 1
        LayerStr += line + "\n"
    # Last Layer
    LayerList.append(LayerStr)

    return LayerList
# ********************************************************************************************************
# * test stuff
# ********************************************************************************************************
if __name__ == '__main__':
    FileNameIn = r"C:\Users\Public\Documents\Python\CuraGcodePost\CE3_Coffee Bin Light No M591.gcode"
    NewList = BuildLayerList(FileNameIn)
    x = 1