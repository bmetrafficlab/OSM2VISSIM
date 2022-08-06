# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 14:27:03 2022

@author: tokes
"""
 
import win32com.client as com
import os
import math
from osgeo import ogr
import shapely.geometry as sg
import pyproj
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import messagebox
# import json

file_window=tk.Tk(className='OSM file')

file_canvas=tk.Canvas(file_window, width=250, height=200)
file_canvas.pack()

file_label=tk.Label(file_window, text='Enter the name of the OSM file', font=('helvetica', 12))
file_canvas.create_window(125, 50, window=file_label)

file_entry=tk.Entry(file_window, width=20)
file_canvas.create_window(125, 100, window=file_entry)

file_entry.insert(0,'BME')

def Set_osm_file(e):
    
    global osm_file
    
    osm_file=file_entry.get()
    
    file_window.destroy()

file_window.bind('<Return>', Set_osm_file)

file_button=tk.Button(file_window, text='Set', command=Set_osm_file, font=('helvetica', 9, 'bold'), bg='brown', fg='white')
file_canvas.create_window(125, 150, window=file_button)

file_window.mainloop()

#Create base .inpx XML file
f= open(str(osm_file)+".osm.inpx","w+")
f.write("<network>\n</network>")
f.close()

# Connnecting COM server
Vissim= com.Dispatch("Vissim.Vissim")

#Get Vissim version for XML file

Filename = os.path.join(os.getcwd(),str(osm_file)+".osm.inpx") # in Current Working Directory 
Vissim.LoadNet(Filename, True)

# ----Base data------
# This base data were added in order to solve fulfill and solve empty file issue
Vissim.Net.VehicleClasses.AddVehicleClass(1)
#Vissim.Net.VehicleTypes.AddVehicleType(1)
##Vissim.Net.TimeDistributions.AddTimeDistributionNormal(1)
##Vissim.Net.DrivingBehaviors.AddDrivingBehavior(1) 
##Vissim.Net.LinkBehaviorTypes.AddLinkBehaviorType(1) 
#Vissim.Net.LinkBehaviorTypes.ItemByKey(1).VehClassDrivBehav.AddVehClassDrivingBehavior(Vissim.Net.VehicleClasses.ItemByKey(30)) 
#Vissim.Net.DisplayTypes.AddDisplayType(1) 
##Vissim.Net.Levels.AddLevel(1)
# --------Links---------------
# Input parameters to add links

# osm_file='BME.osm'

driver=ogr.GetDriverByName('OSM')
data_source = driver.Open(osm_file+'.osm')

tree = ET.parse(osm_file+'.osm')
root = tree.getroot()

no_turn_restrictions=[]
only_restrictions=[]

SH_ID=1

layer = data_source.GetLayer('lines')

features=[x for x in layer]

short_links=0
Links=[]
link_key=1
carways=[]
footways=[]
cycleways=[]
all_cycleway_coords={}
all_carway_coords={}
carways_with_crossing=[]
cycleways_with_crossing=[]

print('Creating links')

# messagebox_window=tk.Tk()

# messagebox_canvas=tk.Canvas(messagebox, width=0, height=0)
# messagebox_canvas.pack()

# tk.messagebox.showinfo(title='Warning', message='Building in progress. Please wait!')

for feature in features:
    
    data=feature.ExportToJson(as_object=True)
    
    way_id=int(data['properties']['osm_id'])
    coords=data['geometry']['coordinates']
    mercator=[]
    other_tags=data['properties']['other_tags']
    name=data['properties']['name']
    highway=data['properties']['highway']
    highways=['steps','footway','cycleway','motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residental', 'motoway_link', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link', 'service', 'track', 'bus_guideway', 'escape', 'raceway', 'road', 'busway', 'living_street', 'residential']
    
    if other_tags and ('"lanes:forward"' in other_tags or '"lanes:backward"' in other_tags or '"turn:lanes:forward"' in other_tags or '"turn:lanes:backward"' in other_tags):
        
        if '"turn:lanes:forward"' in other_tags:
            
            feat=[x for x in other_tags.split(',') if '"turn:lanes:forward"' in x][0]
            lanes_forward=len(feat[feat.rfind('>')+2:feat.rfind('"')].split(';'))
            
            try:
            
                feat=[x for x in other_tags.split(',') if '"lanes"' in x][0]
                lanes_backward=int(feat[feat.rfind('>')+2:feat.rfind('"')])-lanes_forward
            
            except:
                
                try:
                
                    feat=[x for x in other_tags.split(',') if '"turn:lanes:backward"' in x][0]
                    lanes_backward=len(feat[feat.rfind('>')+2:feat.rfind('"')].split(';'))

                except:
                    
                    lanes_backward=0

            
        elif '"turn:lanes:backward"' in other_tags:
            
            feat=[x for x in other_tags.split(',') if '"turn:lanes:backward"' in x][0]
            lanes_backward=len(feat[feat.rfind('>')+2:feat.rfind('"')].split(';'))
            
            try:
            
                feat=[x for x in other_tags.split(',') if '"lanes"' in x][0]
                lanes_forward=int(feat[feat.rfind('>')+2:feat.rfind('"')])-lanes_backward
            
            except:
                
                try:
                
                    feat=[x for x in other_tags.split(',') if '"turn:lanes:forward"' in x][0]
                    lanes_forward=len(feat[feat.rfind('>')+2:feat.rfind('"')].split(';'))
                    
                except:
                    
                    lanes_forward=0
                
        elif '"lanes:forward"' in other_tags:
            
            feat=[x for x in other_tags.split(',') if '"lanes:forward"' in x][0]
            lanes_forward=len(feat[feat.rfind('>')+2:feat.rfind('"')].split(';'))
            
            try:
            
                feat=[x for x in other_tags.split(',') if '"lanes"' in x][0]
                lanes_backward=int(feat[feat.rfind('>')+2:feat.rfind('"')])-lanes_forward
            
            except:
                
                try:
                
                    feat=[x for x in other_tags.split(',') if '"lanes:backward"' in x][0]
                    lanes_backward=len(feat[feat.rfind('>')+2:feat.rfind('"')].split(';'))
            
                except:
                    
                    lanes_backward=0

        elif '"lanes:backward"' in other_tags:
            
            feat=[x for x in other_tags.split(',') if '"lanes:backward"' in x][0]
            lanes_backward=len(feat[feat.rfind('>')+2:feat.rfind('"')].split(';'))
            
            try:
            
                feat=[x for x in other_tags.split(',') if '"lanes"' in x][0]
                lanes_forward=int(feat[feat.rfind('>')+2:feat.rfind('"')])-lanes_backward
            
            except:
                
                try:
                
                    feat=[x for x in other_tags.split(',') if '"lanes:forward"' in x][0]
                    lanes_forward=len(feat[feat.rfind('>')+2:feat.rfind('"')].split(';'))        
                
                except:
                    
                    lanes_forward=1
            
        lanes=0

    else:
        
        try:
        
            feat=[x for x in other_tags.split(',') if '"lanes"' in x][0]
            lanes=int(feat[feat.rfind('>')+2:feat.rfind('"')])
            
        except:
            
            lanes=1
            
        lanes_forward=0
        lanes_backward=0

    def Convert_to_mercator(lat, lon):
        
        RADIUS = 6378137.0
        lat_mer=math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * RADIUS
        lon_mer=math.radians(lon) * RADIUS
        
        return [lon_mer, lat_mer]

    if highway in highways:

        for k in range(len(coords)):
            
            mercator.append(Convert_to_mercator(coords[k][1], coords[k][0]))    

        if highway=='cycleway':
            
            width=1.5

        elif highway=='footway' or highway=='steps':
            
            width=1

        elif other_tags and '"oneway"' in other_tags:
            
            feat=[x for x in other_tags.split(',') if '"oneway"' in x][0]
            oneway=feat[feat.rfind('>')+2:feat.rfind('"')].split(';')[0]
            
            if '"junction"' in other_tags:
                
                oneway='yes'
            
            if oneway=='yes':
                
                width=3.5

            else:

                lanes_forward=1
                lanes_backward=1
                
                if lanes==1:
                
                    width=2.75
                
                else:

                    width=3.5
                    
                lanes=0

        elif other_tags and not('"oneway"' in other_tags):
            
            if '"junction"' in other_tags:

                feat=[x for x in other_tags.split(',') if '"lanes"' in x][0]
                lanes=int(feat[feat.rfind('>')+2:feat.rfind('"')])
                
                width=3.5
                
                lanes_forward=0
                lanes_backward=0
                
            else:
      
                lanes_forward=1
                lanes_backward=1
            
                if lanes==1:
                
                    width=2.75
                
                else:
    
                    width=3.5
                    
                lanes=0
            
        else:
            
            width=3.5
            
        widths=[]

        if width==1.5:
            
            key_list=list(all_cycleway_coords.keys())
            value_list=list(all_cycleway_coords.values())

            for way_1_coords in coords:
                
                for way_2_coords in value_list:
                    
                    if way_1_coords in way_2_coords:

                        cycleways_with_crossing.append([str(way_id), str(key_list[value_list.index(way_2_coords)])])
                        cycleways_with_crossing.append(['-'+str(way_id), str(key_list[value_list.index(way_2_coords)])])
                        cycleways_with_crossing.append([str(way_id), '-'+str(key_list[value_list.index(way_2_coords)])])
                        cycleways_with_crossing.append(['-'+str(way_id), '-'+str(key_list[value_list.index(way_2_coords)])])

            all_cycleway_coords[way_id]=coords
            
        elif width==3.5 or width==2.75:
            
            key_list=list(all_carway_coords.keys())
            value_list=list(all_carway_coords.values())

            for way_1_coords in coords:
                
                for way_2_coords in value_list:
                    
                    if way_1_coords in way_2_coords:

                        carways_with_crossing.append([str(way_id), str(key_list[value_list.index(way_2_coords)])])
                        carways_with_crossing.append(['-'+str(way_id), str(key_list[value_list.index(way_2_coords)])])
                        carways_with_crossing.append([str(way_id), '-'+str(key_list[value_list.index(way_2_coords)])])
                        carways_with_crossing.append(['-'+str(way_id), '-'+str(key_list[value_list.index(way_2_coords)])])
     
            all_carway_coords[way_id]=coords
                
        
        if lanes_forward==0:
        
            for k in range(lanes):
                
                widths.append(width) 
            
        else:
            
            for k in range(lanes_forward):
                
                widths.append(width)
        
        # if mercator!=sorted(mercator) and mercator[::-1]!=sorted(mercator):
        
        #     Links.append(
        #         Vissim.Net.Links.AddLink(way_id, str(sg.LineString(mercator)), widths)
        #         )
            
        # else:
            
        #     Links.append(
        #         Vissim.Net.Links.AddLink(way_id, str(sg.LineString(sorted(mercator))), widths)
        #         )
        
        if mercator[0][0]>=mercator[1][0]  and lanes_backward!=0:
            
            linestring=mercator[::-1]

        else:
            
            linestring=mercator
            
        Links.append(
            Vissim.Net.Links.AddLink(way_id, str(sg.LineString(linestring)), widths)
            )
        
        Links[-1].SetAttValue('Name', way_id)
        
        # if Links[-1].AttValue('Length2D')<5:
            
        #     Vissim.Net.Links.RemoveLink(Links[-1])
            
        #     del Links[-1]
            
        #     continue

        if width==3.5 or width==2.75:
            
            carways.append(Links[-1])
            
        elif width==1.5:
            
            cycleways.append(Links[-1])
            
        else:

            footways.append(Links[-1])
        
        if lanes_forward!=0:

            Links.append(
                Vissim.Net.Links.GenerateOppositeDirection(Vissim.Net.Links.ItemByKey(way_id), lanes_backward)
                )
            
            Links[-1].SetAttValue('Name', -way_id)
            
            if width==3.5 or width==2.75:
                
                carways.append(Links[-1])
                
            elif width==2:
                
                cycleways.append(Links[-1])
                
            else:

                footways.append(Links[-1])
            
            link_key=link_key+1
        
        link_key=link_key+1

for link_no in range(short_links):
    
    Vissim.Net.Links.RemoveLink(Vissim.Net.Links.ItemByKey(link_no+1))

def Create_connectors(way_type):
    
    if way_type==carways:
  
        way_2_list=carways_with_crossing

        print('Creating carway connectors')
        
    elif way_type==cycleways:
        
        way_2_list=cycleways_with_crossing
        
        print('Creating cycleway connectors')
    
    serial_number=0
    
    percentages=[]
    
    for way_1 in way_type:

        percentage=serial_number/len(way_type)*100

        if int(percentage)%10==0 and not(int(percentage) in percentages):
            
            percentages.append(int(percentage))
            
            print("%.2f" % int(percentage)+"%")
            
        serial_number=serial_number+1
        
        if only_restrictions!=[]:
        
            for restriction in only_restrictions:
                
                if restriction[0]==int(way_1.AttValue('Name')):
                    
                    has_rest=True
    
                    break
                
                else:
    
                    has_rest=False
                    
        else:
            
            has_rest=False

        linkpolypts_1=way_1.LinkPolyPts.GetAll()
        
        coord_x_1=linkpolypts_1[-1].AttValue('X')
        coord_y_1=linkpolypts_1[-1].AttValue('Y')
        
        way_1_start=[linkpolypts_1[0].AttValue('X'), linkpolypts_1[0].AttValue('Y')]
        
        for way_2 in way_type:             
            
            if way_2.AttValue('Length2D')<=5 or way_1.AttValue('Length2D')<=5:
                
                dist=3
                
            else:
                
                dist=5

            if [way_1.AttValue('Name'), way_2.AttValue('Name')] in way_2_list or [way_2.AttValue('Name'), way_1.AttValue('Name')] in way_2_list:

                pass
            
            else:
                
                continue

            if has_rest and not([int(way_1.AttValue('Name')),int(way_2.AttValue('Name'))] in only_restrictions):
    
                continue

            # way_2_start=[way_2.LinkPolyPts.GetAll()[0].AttValue('X'),way_2.LinkPolyPts.GetAll()[0].AttValue('Y')]
            
            # way_2_end=[way_2.LinkPolyPts.GetAll()[-1].AttValue('X'),way_2.LinkPolyPts.GetAll()[-1].AttValue('Y')]

            # if len(way_2.LinkPolyPts.GetAll())>2:
                   
            #     cycle_length=len(way_2.LinkPolyPts.GetAll())-1
                                    
            # else:
        
            #     cycle_length=1    
        
            for linkpoly_2_index in range(len(way_2.LinkPolyPts.GetAll())):

                linkpoly_2=way_2.LinkPolyPts.GetAll()[linkpoly_2_index]
                
                coord_x_2=linkpoly_2.AttValue('X')
                coord_y_2=linkpoly_2.AttValue('Y')

                if linkpoly_2_index!=len(way_2.LinkPolyPts.GetAll())-1 and way_1!=way_2 and int(way_1.AttValue('Name'))!=-int(way_2.AttValue('Name')) and not([int(way_1.AttValue('Name')),int(way_2.AttValue('Name'))] in no_turn_restrictions) and math.dist([coord_x_1, coord_y_1], [coord_x_2, coord_y_2])<dist:

                    polypoints=way_2.LinkPolyPts.GetAll()
                    
                    points_for_link=polypoints[0:linkpoly_2_index+1]
                    
                    coords_for_link=[]
                    
                    for point in range(len(points_for_link)):
                        
                        coords_for_link.append([points_for_link[point].AttValue('X'), points_for_link[point].AttValue('Y')])
                    
                    if linkpoly_2_index!=0:
                
                        Links.append(
                            Vissim.Net.Links.AddLink(0, str(sg.LineString(coords_for_link)), [3.5])
                            )
                        
                    lanes=min(way_1.AttValue('NumLanes'), way_2.AttValue('NumLanes'))
                    
                    if lanes==1:
                    
                        lane_connection_1=1
                        lane_connection_2=1
                        
                    else: 
                        
                        lane_connection_1=way_1.AttValue('NumLanes')-lanes+1
                        lane_connection_2=way_2.AttValue('NumLanes')-lanes+1
                    
                    if linkpoly_2_index!=0 and linkpoly_2_index!=len(way_2.LinkPolyPts.GetAll())-2:
                        
                        connect_pos=Links[-1].AttValue('Length2D')+5
                        
                    elif linkpoly_2_index!=0:
                        
                        connect_pos=Links[-1].AttValue('Length2D')+1
                        
                    else:
                                    
                        if way_2.AttValue('Length2D')<3:
                            
                            connect_pos=1
        
                        elif way_2.AttValue('Length2D')<5:
                            
                            connect_pos=2
        
                        else:
                            
                            connect_pos=5
                            
                    Vissim.Net.Links.AddConnector(0,way_1.Lanes.ItemByKey(lane_connection_1), way_1.AttValue('Length2D'), way_2.Lanes.ItemByKey(lane_connection_2), connect_pos, lanes, 'LINESTRING EMPTY')
                
                    if linkpoly_2_index!=0:
                    
                        Vissim.Net.Links.RemoveLink(Links[-1])

                    break 
                
                if linkpoly_2_index!=len(way_2.LinkPolyPts.GetAll())-1 and linkpoly_2_index!=len(way_2.LinkPolyPts.GetAll())-2 and linkpoly_2_index!=1 and linkpoly_2_index!=0 and way_1!=way_2 and int(way_1.AttValue('Name'))!=-int(way_2.AttValue('Name')) and not([int(way_2.AttValue('Name')),int(way_1.AttValue('Name'))] in no_turn_restrictions) and math.dist(way_1_start, [coord_x_2, coord_y_2])<dist:

                    polypoints=way_2.LinkPolyPts.GetAll()
                    
                    points_for_link=polypoints[0:linkpoly_2_index+1]
                    
                    coords_for_link=[]
                    
                    for point in range(len(points_for_link)):
                        
                        coords_for_link.append([points_for_link[point].AttValue('X'), points_for_link[point].AttValue('Y')])
                    
                    if linkpoly_2_index!=1:
                
                        Links.append(
                            Vissim.Net.Links.AddLink(0, str(sg.LineString(coords_for_link)), [3.5])
                            )
                        
                    lanes=min(way_1.AttValue('NumLanes'), way_2.AttValue('NumLanes'))
                    
                    if lanes==1:
                    
                        lane_connection_1=1
                        lane_connection_2=1
                        
                    else: 
                        
                        lane_connection_1=way_1.AttValue('NumLanes')-lanes+1
                        lane_connection_2=way_2.AttValue('NumLanes')-lanes+1

                    connect_pos=Links[-1].AttValue('Length2D')-3

                    Vissim.Net.Links.AddConnector(0, way_2.Lanes.ItemByKey(lane_connection_2), connect_pos, way_1.Lanes.ItemByKey(lane_connection_1), 3, lanes, 'LINESTRING EMPTY')

                    if linkpoly_2_index!=0:
                    
                        Vissim.Net.Links.RemoveLink(Links[-1])
                  
                    break 

print('Creating signal heads')

lamp_coords={}

for nodes in root:
    
    if nodes.tag=='node':
    
        for node in nodes:
            
            if node.attrib['v']=='traffic_signals':
                
                lamp_id=nodes.attrib['id']

                for ways in root:
                    
                    if ways.tag=='way':
                        
                        for way in ways:

                            if 'ref' in way.attrib and way.attrib['ref']==lamp_id:                            

                                SC_near=False
                                
                                SC_found=False
                                
                                way_id=ways.attrib['id']

                                if lamp_id in lamp_coords:
                                    
                                    SC_ID=list(lamp_coords).index(lamp_id)+1

                                    SC_found=True
                                    
                                else:
                                    
                                    for coords in lamp_coords:
                                        
                                        if math.dist(Convert_to_mercator(float(nodes.attrib['lat']), float(nodes.attrib['lon'])), lamp_coords[coords])<30:
                                            
                                            SC_ID=list(lamp_coords).index(coords)+1

                                            SC_found=True
                                            
                                            SC_near=True
                                            
                                            break
                                    
                                        SC_found=False

                                if not(SC_found):

                                    SC_ID=len(Vissim.Net.SignalControllers)+1

                                    Vissim.Net.SignalControllers.AddSignalController(SC_ID)

                                Vissim.Net.SignalControllers.ItemByKey(SC_ID).SGs.AddSignalGroup(len(Vissim.Net.SignalControllers.ItemByKey(SC_ID).SGs)+1)

                                for link in Vissim.Net.Links:

                                    if link.AttValue('Name')==way_id:
                                
                                        linkpolypts_1=link.LinkPolyPts.GetAll()

                                        break

                                for link in Vissim.Net.Links:
                                        
                                    if link.AttValue('Name')=='-'+way_id:
                                        
                                        linkpolypts_2=link.LinkPolyPts.GetAll()
                                 
                                        oneway=False
                                        
                                        break
                                        
                                    else:
                                        
                                        oneway=True

                                link_start_1=[linkpolypts_1[-1].AttValue('X'), linkpolypts_1[-1].AttValue('Y')]
                                
                                try:
                                
                                    link_start_2=[linkpolypts_2[-1].AttValue('X'), linkpolypts_2[-1].AttValue('Y')]                                   
                                
                                except:
                                    
                                    pass
                                
                                if oneway:
                                    
                                    link_name=way_id
                                    
                                else:
                                
                                    if math.dist(Convert_to_mercator(float(nodes.attrib['lat']), float(nodes.attrib['lon'])), link_start_1)<math.dist(Convert_to_mercator(float(nodes.attrib['lat']), float(nodes.attrib['lon'])), link_start_2):

                                        link_name=way_id

                                    else:
                                        
                                        link_name='-'+way_id
                                
                                for link in Vissim.Net.Links:
                                    
                                    try:
                                    
                                        if link.AttValue('Name')==link_name:
                                            
                                                polypoints=link.LinkPolyPts.GetAll()
                                                
                                                for point_index in range(len(polypoints)):
                                                    
                                                    if point_index!=0:
                                                        
                                                        if math.dist(Convert_to_mercator(float(nodes.attrib['lat']), float(nodes.attrib['lon'])), [polypoints[point_index].AttValue('X'), polypoints[point_index].AttValue('Y')])<math.dist(Convert_to_mercator(float(nodes.attrib['lat']), float(nodes.attrib['lon'])), [polypoints[point_index-1].AttValue('X'), polypoints[point_index-1].AttValue('Y')]):
                                                            
                                                            closest_point=polypoints[point_index]
                                                            
                                                    else:
                                                        
                                                        pass
        
                                                points_for_link=polypoints[0:polypoints.index(closest_point)+1]
                                                
                                                coords_for_link=[]
                                                
                                                for point in range(len(points_for_link)):
                                                    
                                                    coords_for_link.append([points_for_link[point].AttValue('X'), points_for_link[point].AttValue('Y')])

                                                Links.append(
                                                    Vissim.Net.Links.AddLink(0, str(sg.LineString(coords_for_link)), [3.5])
                                                    )
                                                
                                                for lane in link.Lanes:
        
                                                    Vissim.Net.SignalHeads.AddSignalHead(SH_ID, lane, Links[-1].AttValue('Length2D')-5)
                                                    Vissim.Net.SignalHeads.ItemByKey(SH_ID).SetAttValue('SG', Vissim.Net.SignalControllers.ItemByKey(SC_ID).SGs.ItemByKey(len(Vissim.Net.SignalControllers.ItemByKey(SC_ID).SGs)))
                                                    SH_ID=SH_ID+1
                                                    
                                                Vissim.Net.Links.RemoveLink(Links[-1])
                                        
                                        if not(lamp_id in lamp_coords) and not(SC_near):
                                        
                                            lamp_coords[nodes.attrib['id']]=Convert_to_mercator(float(nodes.attrib['lat']), float(nodes.attrib['lon']))
                                        
                                        
                                        
                                    except:
                                        
                                        pass

for relations in root:

    if relations.tag=='relation':
    
        for relation in relations:
            
            if 'k' in relation.attrib:

                if relation.attrib['k']=='restriction' and (relation.attrib['v']=='no_right_turn' or relation.attrib['v']=='no_left_turn'):

                    for ways in relations:
                        
                        if 'role' in ways.attrib:

                            if ways.attrib['role']=='from':
                            
                                from_way_id=int(ways.attrib['ref'])
                                
                            if ways.attrib['role']=='to':
                            
                                to_way_id=int(ways.attrib['ref'])
                                
                        else:
                            
                            continue
                                
                    no_turn_restrictions.append([from_way_id, to_way_id])
                    no_turn_restrictions.append([-from_way_id, to_way_id])
                    no_turn_restrictions.append([from_way_id, -to_way_id])
                    no_turn_restrictions.append([-from_way_id, -to_way_id])
                        
                if relation.attrib['k']=='restriction' and (relation.attrib['v']=='only_straight_on' or relation.attrib['v']=='only_right_turn' or relation.attrib['v']=='only_left_turn'):
            
                    for ways in relations:
                        
                        if 'role' in ways.attrib:

                            if ways.attrib['role']=='from':
                            
                                from_way_id=int(ways.attrib['ref'])
                                
                            if ways.attrib['role']=='to':
                                
                                to_way_id=int(ways.attrib['ref'])
                                
                        else:
                            
                            continue
                                
                    only_restrictions.append([from_way_id, to_way_id])
                    only_restrictions.append([-from_way_id, to_way_id])
                    only_restrictions.append([from_way_id, -to_way_id])
                    only_restrictions.append([-from_way_id, -to_way_id])


Create_connectors(cycleways)

print('100.0%')

Create_connectors(carways)

print('100.0%')

Vissim.SaveNetAs(os.path.join(os.getcwd(), str(osm_file)+".inpx"))

done_window=tk.Tk(className='Done')

done_canvas=tk.Canvas(done_window, width=250, height=200)
done_canvas.pack()

input("Press 'Enter' to exit")

Vissim.SaveNetAs(os.path.join(os.getcwd(),str(osm_file)+".inpx"))
