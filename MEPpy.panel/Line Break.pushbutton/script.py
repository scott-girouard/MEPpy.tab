__title__ = "Line Break"
__author__ = "Scott Girouard"
__doc__ = """Version 1.0
_____________________________________________________________________
Description:
This tool creates a line break for two intersecting lines. 
_____________________________________________________________________
How-to
Drag to select two intersection lines. 
"""
#References
from gettext import translation
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
delta   = 2 # Offset distance

# Select model elements - selec two intersecting line
def element_selection():
    try:
        with forms.WarningBar(title="Pick elements"):
            reference = uidoc.Selection.PickObjects(Selection.ObjectType.Element, 'Choose elements')
    except Exceptions.OperationCanceledException:
        return False

    try:
        el1 = doc.GetElement(reference[0])
    except Exceptions.OperationCanceledException:
        return True

    try:
        el2 = doc.GetElement(reference[1])
    except Exceptions.OperationCanceledException:
        return True

    # Get the start & end points of each line
    ds1StartPoint = get_start(el1)
    ds1EndPoint = get_end(el1)
    rvtCrv1 = el1.Location.Curve

    ds2StartPoint = get_start(el2)
    ds2EndPoint = get_end(el2)
    rvtCrv2 = el2.Location.Curve

    # Get the intersection point of the two lines
    intersection = rvtCrv1.Intersect(rvtCrv2)

    # Find line intersections:
    p1 = rvtCrv1.GetEndPoint( 0 )
    q1 = rvtCrv1.GetEndPoint( 1 )
    p2 = rvtCrv2.GetEndPoint( 0 )
    q2 = rvtCrv2.GetEndPoint( 1 )
    v1 = q1 - p1
    v2 = q2 - p2
    w = p2 - p1
    c = ( v2.X * w.Y - v2.Y * w.X ) / ( v2.X * v1.Y - v2.Y * v1.X )
    x = p1.X + c * v1.X
    y = p1.Y + c * v1.Y
    p5 = XYZ( x, y, 0 )

    # Create lines based on points:
    ln1Start = XYZ(p1.X, p1.Y, 0)
    ln1End = XYZ(p5.X - delta, p1.Y, 0)
    ln2Start = XYZ(p5.X + delta, p1.Y, 0)
    ln2End = XYZ(q1.X, p1.Y, 0)

    t = Transaction(doc, 'New line 1')
    t.Start()
    line1 = Line.CreateBound(ln1Start, ln1End)
    line2 = Line.CreateBound(ln2Start, ln2End)
    t.Commit()

    #Create a sketch plane
    origin = XYZ.Zero
    normal = XYZ.BasisZ
    t = Transaction(doc, 'Create sketch plane')
    t.Start()
    plane = Autodesk.Revit.DB.Plane.CreateByNormalAndOrigin(normal,origin)
    skplane = SketchPlane.Create(doc, plane)
    crv1 = doc.Create.NewModelCurve(line1, skplane)
    crv2 = doc.Create.NewModelCurve(line2, skplane)

    # Reference original line style to match
    set_lineStyle(el1, crv1)
    set_lineStyle(el2, crv2)
    
    # Delete original line
    deletedLine = delete_line(reference[0])
    t.Commit()

def set_lineStyle(element, curve):
    lineStyleBase = element.LookupParameter("Line Style")
    graphicType = element.LineStyle
    curve.LineStyle = graphicType

def delete_line(element):
    elID = element.ElementId
    deletedLine = doc.Delete(elID)

# Get the start point of line
def get_start(element):
    rvtCrv1 = element.Location.Curve
    ds1Crv = rvtCrv1.ToProtoType()
    ds1StartPoint = ds1Crv.StartPoint
    return ds1StartPoint

# Get the end point of line
def get_end(element):
    rvtCrv1 = element.Location.Curve
    ds1Crv = rvtCrv1.ToProtoType()
    ds1EndPoint = ds1Crv.EndPoint
    return ds1EndPoint

while element_selection():
    pass

#=================================================
""" TO DO LIST:
    - Remove proto reference. Dynamo must be open for the script to run. 
    - Determine line to be broken by horizontal vector. Line broken should always be the horizontal line.
    - Allow multiple interecting lines to be broken upon selection.
    - Add GUI for delta offset value update update.
"""

