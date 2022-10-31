import arcpy 
import pandas as pd

# Define bus lanes and bus routes layer name
bus_lanes = "geo_export_95b69495-f013-49b8-9264-2f0d0e49abfa"
bus_routes = "routes_buffer_80"

# Add a route and direction field as "route_na"
arcpy.management.CalculateField(bus_routes, "route_na", "!route_id! + ' ' + str(!direction_id!)", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

# Add SPA_DIR to bus routes layer from Bus Trips Average

# Define location of buffers and join output
bus_lane_buff = r"C:\Users\1280530\GIS\Bus Lanes\01_Data\Bus_Lanes.gdb\bus_lanes_25_buffer"
route_buff = r"C:\Users\1280530\GIS\Bus Lanes\01_Data\Bus_Lanes.gdb\bus_routes_80buf"
buslane_join =  r"C:\Users\1280530\GIS\Bus Lanes\01_Data\Bus_Lanes.gdb\lane_routes_join_v2"

# Buffer bus lanes
arcpy.analysis.PairwiseBuffer(bus_lanes, bus_lane_buff, "25 Feet", "NONE", None, "PLANAR", "0 DecimalDegrees")

# Buffer bus routes
arcpy.analysis.PairwiseBuffer(bus_routes, route_buff, "80 Feet", "NONE", None, "PLANAR", "0 DecimalDegrees")

# Define field mapping
fieldmapping = 'street "street" true true false 254 Text 0 0,First,#,buslanes_buffer25,street,0,254;bltrafdir "bltrafdir" true true false 254 Text 0 0,First,#,buslanes_buffer25,bltrafdir,0,254;segmentid "segmentid" true true false 254 Text 0 0,First,#,buslanes_buffer25,segmentid,0,254;rw_type "rw_type" true true false 254 Text 0 0,First,#,buslanes_buffer25,rw_type,0,254;streetwidt "streetwidt" true true false 8 Double 0 0,First,#,buslanes_buffer25,streetwidt,-1,-1;bor_ "bor_" true true false 254 Text 0 0,First,#,buslanes_buffer25,bor_,0,254;facility "facility" true true false 254 Text 0 0,First,#,buslanes_buffer25,facility,0,254;hours "hours" true true false 254 Text 0 0,First,#,buslanes_buffer25,hours,0,254;days "days" true true false 254 Text 0 0,First,#,buslanes_buffer25,days,0,254;lane_type "lane_type" true true false 254 Text 0 0,First,#,buslanes_buffer25,lane_type,0,254;open_date "open_date" true true false 254 Text 0 0,First,#,buslanes_buffer25,open_date,0,254;year1 "year1" true true false 8 Double 0 0,First,#,buslanes_buffer25,year1,-1,-1;year2 "year2" true true false 8 Double 0 0,First,#,buslanes_buffer25,year2,-1,-1;year3 "year3" true true false 8 Double 0 0,First,#,buslanes_buffer25,year3,-1,-1;fac_type1 "fac_type1" true true false 254 Text 0 0,First,#,buslanes_buffer25,fac_type1,0,254;fac_type2 "fac_type2" true true false 254 Text 0 0,First,#,buslanes_buffer25,fac_type2,0,254;sbs_route1 "sbs_route1" true true false 254 Text 0 0,First,#,buslanes_buffer25,sbs_route1,0,254;sbs_route2 "sbs_route2" true true false 254 Text 0 0,First,#,buslanes_buffer25,sbs_route2,0,254;sbs_route3 "sbs_route3" true true false 254 Text 0 0,First,#,buslanes_buffer25,sbs_route3,0,254;days_code "days_code" true true false 8 Double 0 0,First,#,buslanes_buffer25,days_code,-1,-1;last_updat "last_updat" true true false 254 Text 0 0,First,#,buslanes_buffer25,last_updat,0,254;prim_color "prim_color" true true false 254 Text 0 0,First,#,buslanes_buffer25,prim_color,0,254;minofyea_1 "minofyea_1" true true false 8 Double 0 0,First,#,buslanes_buffer25,minofyea_1,-1,-1;chron_id_1 "chron_id_1" true true false 254 Text 0 0,First,#,buslanes_buffer25,chron_id_1,0,254;shape_leng "shape_leng" true true false 8 Double 0 0,First,#,buslanes_buffer25,shape_leng,-1,-1;shape_le_1 "shape_le_1" true true false 8 Double 0 0,First,#,buslanes_buffer25,shape_le_1,-1,-1;BUFF_DIST "BUFF_DIST" true true false 8 Double 0 0,First,#,buslanes_buffer25,BUFF_DIST,-1,-1;ORIG_FID "ORIG_FID" true true false 4 Long 0 0,First,#,buslanes_buffer25,ORIG_FID,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,buslanes_buffer25,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,buslanes_buffer25,Shape_Area,-1,-1;route_id "route_id" true true false 20 Text 0 0,First,#,bus_routes_50buf,route_id,0,20;direction_id "direction_id" true true false 1 Text 0 0,First,#,bus_routes_50buf,direction_id,0,1;shape_id "shape_id" true false false 20 Text 0 0,First,#,bus_routes_50buf,shape_id,0,20;zip_name "zip_name" true false false 40 Text 0 0,First,#,bus_routes_50buf,zip_name,0,40;agency_name "agency_name" true true false 6 Text 0 0,First,#,bus_routes_50buf,agency_name,0,6;sample_gtfs_trip_id "sample_gtfs_trip_id" true true false 255 Text 0 0,First,#,bus_routes_50buf,sample_gtfs_trip_id,0,255;destination_headsign "destination_headsign" true true false 255 Text 0 0,First,#,bus_routes_50buf,destination_headsign,0,255;number_of_trips "number_of_trips" true true false 4 Long 0 0,First,#,bus_routes_50buf,number_of_trips,-1,-1;BUFF_DIST_1 "BUFF_DIST" true true false 8 Double 0 0,First,#,bus_routes_50buf,BUFF_DIST,-1,-1;ORIG_FID_1 "ORIG_FID" true true false 4 Long 0 0,First,#,bus_routes_50buf,ORIG_FID,-1,-1;route_na "route_na" true true false 255 Text 0 0,First,#,bus_routes_50buf,route_na,0,255;Shape_Length_1 "Shape_Length" false true true 8 Double 0 0,First,#,bus_routes_50buf,Shape_Length,-1,-1;Shape_Area_1 "Shape_Area" false true true 8 Double 0 0,First,#,bus_routes_50buf,Shape_Area,-1,-1;routes_ser "routes_ser" true true false 1000 Text 0 0,Join,";"'
# Create a fieldmappings
fieldmappings = arcpy.FieldMappings()
# Adding a table is the fast way to load all the fields from the input 
# into fieldmaps held by the fieldmappings object.
for fc in [bus_lane_buff]:
    fieldmappings.addTable(fc)

# Join routes to bus lanes layer
arcpy.analysis.SpatialJoin("buslanes_buffer25", "bus_routes_50buf", buslane_join, "JOIN_ONE_TO_ONE", "KEEP_ALL", 
fieldmapping,"WITHIN", None, '')

def deleteextrafields(out_fc, orig_fc, joined_fc,): 
    # Get list of fields for inputs and outputs
    out_fields = [f.name for f in arcpy.ListFields(out_fc)]
    lane_fields = [f.name for f in arcpy.ListFields(orig_fc)]
    route_fields = [f.name for f in arcpy.ListFields(joined_fc)]
    # Find list of fields to delete
    matchedfields = [f for f in out_fields if f in route_fields]
    extrafields = [f for f in matchedfields if f not in ['OBJECTID', 'Shape', 'BUFF_DIST','Shape_Length', 'Shape_Area']]
    print('To delete: ', extrafields)
    # Delete extraneous route data fields
    arcpy.management.DeleteField(buslane_join, extrafields, method='DELETE_FIELDS')

deleteextrafields(buslane_join, bus_lane_buff, route_buff)

def returnunique(routes_string):
    if isinstance(routes_string, str):
        routes = routes_string.split(';')
        return ';'.join(list(set(routes)))
    else:
        return routes_string
    
def removedirection(routes_string):
    if isinstance(routes_string, str):
        routes = routes_string.split(';')
        routeslist = []
        for r in routes:
            if r[-2:] == ' 1' or r[-2:] == ' 0':
                routeslist.append(r[:-2])
            else:
                routeslist.append(r)
        return ';'.join(list(set(routeslist)))
    else:
        return routes_string

returnuniquestring = '''def returnunique(routes_string):
    if isinstance(routes_string, str):
        routes = routes_string.split(';')
        return ';'.join(list(set(routes)))
    else:
        return routes_string'''

removedirectionstring = '''def removedirection(routes_string):
    if isinstance(routes_string, str):
        routes = routes_string.split(';')
        routeslist = []
        for r in routes:
            if r[-2:] == ' 1' or r[-2:] == ' 0':
                routeslist.append(r[:-2])
            else:
                routeslist.append(r)
        return ';'.join(list(set(routeslist)))
    else:
        return routes_string'''

arcpy.management.CalculateField(buslane_join, 'routes_ser', "returnunique(!routes_ser!)", 
                                expression_type="PYTHON3", code_block=returnuniquestring)

# Add new route_nodirection field
arcpy.management.AddField(buslane_join, 'routes_nod', "TEXT", field_length=1000)

arcpy.management.CalculateField(buslane_join, 'routes_nod', "removedirection(!routes_ser!)", 
                                expression_type="PYTHON3", code_block=removedirectionstring)

def writematchingdata(todata_fc, fromdata_fc, joinfield, adddatafield):
    datadict = {}
    if isinstance(joinfield, tuple): # If the join field isn't the same between fcs, use a tuple
        joinfield = joinfield[0]
        targetfield = joinfield[1]
    else:
        targetjoin = joinfield
    with arcpy.da.SearchCursor(fromdata_fc, [joinfield,adddatafield]) as cursor:
        for row in cursor:
            datadict[row[0]] = row[1]
    newfield = [f for f in arcpy.ListFields(fromdata_fc) if f.name == adddatafield][0]
    if newfield not in [f.name for f in arcpy.ListFields(todata_fc)]:
        arcpy.management.AddField(todata_fc, field_name=adddatafield, field_type=newfield.type, field_length=newfield.length, field_is_nullable=newfield.isNullable)
    with arcpy.da.UpdateCursor(todata_fc, [targetjoin,adddatafield]) as cursor:
        for row in cursor:
            row[1] = datadict[row[0]]
            cursor.updateRow(row)

writematchingdata('Bus_Lanes_Segments',buslane_join,'segmentid','routes_ser')

writematchingdata('Bus_Lanes_Segments',buslane_join,'segmentid','routes_nod')