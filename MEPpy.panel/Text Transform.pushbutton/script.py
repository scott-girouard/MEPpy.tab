__title__ = "Text Transform"
__author__ = "Scott Girouard"
__doc__ = """Version 1.0
_____________________________________________________________________
Description:
This tool converts multiple single line text notes into a single multi-line text note.
_____________________________________________________________________
How-to
Drag to select multiple text notes in a document. The notes will then be converted to 
a singular multiline text note. 

"""
#References
import sys
import clr
import re
clr.AddReference('RevitAPIUI')
clr.AddReference('RevitAPI')
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import Point as dsPoint
clr.AddReference('RevitNodes')
from Autodesk.DesignScript.Geometry import *
import Autodesk
import Revit
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

from Autodesk.Revit.DB import Line, ViewSection, XYZ, FilteredElementCollector, Grid, ReferencePlane, FamilyInstance, \
    BuiltInParameter, ElevationMarker, ViewType
from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit import Exceptions

clr.AddReference('DSCoreNodes')
import DSCore
from DSCore import *

import rpw
from pyrevit import forms, script

clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from System.Collections.Generic import List
clr.ImportExtensions(Revit.GeometryConversion)
clr.ImportExtensions(Revit.Elements)

#Variables
doc     = __revit__.ActiveUIDocument.Document
uidoc   = __revit__.ActiveUIDocument
app     = __revit__.Application

def element_selection():
    try:
        with forms.WarningBar(title="Pick reference element"):
            reference = uidoc.Selection.PickObjects(Selection.ObjectType.Element, 'Choose elements')
    except Exceptions.OperationCanceledException:
        return False

    try:
        element1 = doc.GetElement(reference[0])
    except Exceptions.OperationCanceledException:
        return True

    els = [doc.GetElement( elId ) for elId in reference]
    t = Transaction(doc, 'selection')
    t.Start()
    # Lists
    name = []
    value = []
    ElementIDs=[]
    dataX=[]
    dataY=[]
    dataZ=[]
    tagXYZs = []
    strlist = []
    textNoteText = []

    IDS = List[Autodesk.Revit.DB.ElementId]()

    for i in els:
        IDS.Add(i.Id)

    for i in els:
        ElementIDs.append(i.Id)

    for i in els:
        par1 = i.get_Parameter(BuiltInParameter.TEXT_TEXT)
        name.append(par1.Definition.Name)
        value.append(par1.AsString())
    par2 = els[0].get_Parameter(BuiltInParameter.TEXT_TEXT)
    t.Commit()

    #=======================

    for i in els:
        tagXYZs.append(i.Coord)

    ind=0

    for v in tagXYZs:
        strlist.append(v.ToString())

    for s in strlist:
        data=String.Split(s,"X = ","Y = ","Z = ",",","))")
        dataX.append(DSCore.List.GetItemAtIndex(data,1))
        dataY.append(DSCore.List.GetItemAtIndex(data,1))
        dataZ.append(DSCore.List.GetItemAtIndex(data,1))
	
    for x,y,z in zip(dataX,dataY,dataZ):
        indx=DSCore.List.GetItemAtIndex(dataX,ind)
        indy=DSCore.List.GetItemAtIndex(dataY,ind)
        indz=DSCore.List.GetItemAtIndex(dataZ,ind)

    # Get max Y index value
    maxY = max(dataY)
    maxYindex = dataY.index(maxY)

    # Establish teextnote start location
    textNoteXYZ = strlist[maxYindex]
    defaultTextTypeId = doc.GetDefaultElementTypeId(ElementTypeGroup.TextNoteType)
    opts = TextNoteOptions(defaultTextTypeId)

    for q in els:
        gft = q.GetFormattedText()
        txt = q.Text
        textNoteText.append(txt)

    # Join text of individual text notes
    str = "\n".join(textNoteText)

    # Transaction: Create new textnote
    t = Transaction(doc, 'Name')
    t.Start()
    newNote = TextNote.Create(doc, doc.ActiveView.Id, tagXYZs[maxYindex], 0.614135111876076, str, opts)
    t.Commit()

    # Transaction: Delete old single line text notes
    t = Transaction(doc, 'Delete')
    t.Start()
    doc.Delete(IDS)
    t.Commit()

while element_selection():
    pass