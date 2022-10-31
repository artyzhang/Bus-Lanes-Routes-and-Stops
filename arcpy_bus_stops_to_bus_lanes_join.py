# Bus stop to routes join
import arcpy 
import pandas as pd

'''Part 1: Run one-to-many spatial join'''

def make_field_map(inputDataset, sourceField): # Make a single field as a field map object
    fmap = arcpy.FieldMap()
    # Add source field as input field
    fmap.addInputField(inputDataset, sourceField)
    # New outputField object
    outField = fmap.outputField
    # Set name to equal source
    outField.name = sourceField
    # Set the output to the new output object
    fmap.outputField = outField
    return fmap

def makefieldmappings(leftfc, rightfc, rightfieldstojoin): # Make a fieldmapping object with all left fields and selected right fields
    # Create FieldMappings object
    fieldmappings = arcpy.FieldMappings()
    # Add all existing 
    fieldmappings.addTable(leftfc)
    # Print the field names for the data to be joined
    joinListFields = arcpy.ListFields(rightfc)
    print('All right fields: ', [f.name for f in joinListFields])
    print('Selected right fields: ', rightfieldstojoin)
    # Add the fields we want joined to field mapping object
    for fname in rightfieldstojoin:
        fieldmappings.addFieldMap(make_field_map(lane_segments, fname))
    return fieldmappings

def runspatialjoin(leftfc, rightfc, rightfieldstojoin, outfc):
    fieldmappings = makefieldmappings(leftfc, rightfc, rightfieldstojoin)
    arcpy.analysis.SpatialJoin(bus_stops, lane_segments, outfc, join_operation='JOIN_ONE_TO_MANY',join_type='KEEP_COMMON',field_mapping=fieldmappings,
    match_option='WITHIN_A_DISTANCE',search_radius='80 FEET')

lane_segments = r'C:\Users\1280530\GIS\Bus Lanes\01_Data\Bus_Lanes.gdb\Bus_Lanes_Segments'
bus_stops = r'C:\Users\1280530\GIS\GTFS to Feature Class\Points_Near.gdb\bus_patternstops_202206'
# Define the fields we want joined
tojoinfields = ['street','segmentid','facility', 'hours','routes_ser', 'routes_nod']
spatialjoin_fc = r'C:\Users\1280530\GIS\Bus Lanes\01_Data\Bus_Lanes.gdb\stops_buslanes_manyjoin_test'

# Run the spatial join
#runspatialjoin(bus_stops, lane_segments, tojoinfields, spatialjoin_fc)

'''Part 2: Write spatial join results to dataframe and verify that route name and direction is correct'''

def fc_to_df(fc): # Write feature class to a dataframe
    fields = [f.name for f in arcpy.ListFields(fc)]
    dfconstruct = []
    with arcpy.da.SearchCursor(fc, fields) as cursor:
        for row in cursor:
            values = {}
            for i, field in enumerate(fields):
                values[field] = row[i]
            dfconstruct.append(values)
    return pd.DataFrame(dfconstruct)

# Run the fc to dataframe script
df = fc_to_df(spatialjoin_fc)

def returndirection(value): # See if direction is in a string
    directions = ['NB','SB','EB','WB']
    for d in directions:
        if d in value:
            return d
        else:
            return 'Both'

def make_newfields(df): # Make route name, lane direction, and routes list fields
    # Filter out stop IDs that weren't joined to a bus lane that serves routes
    join_df = df.loc[df['routes_ser'] == df['routes_ser']].copy()
    # Create route + direction field called 'route_name'
    join_df['route_name'] = join_df.apply(lambda x: str(x['route_id']) + ' ' + str(x['direction_id']), axis=1)
    # Find the direction of the bus lane
    join_df['lane_direction'] = join_df.loc[:,'facility'].apply(lambda x: returndirection(x))
    # Split routes_served into a list
    join_df['routes_list'] = join_df.loc[:,'routes_ser'].apply(lambda x: x.split(';'))
    return join_df

def filteronlymatching(df): # Make sure only matching route and direction fields are included
    # Check to make sure the bus stop's route_name matches the list of routes that bus lane serves
    matchedroute = df[df.apply(lambda x: x['route_id'] in x['routes_ser'], axis = 1)]
    matcheddirection = matchedroute[matchedroute.apply(lambda x: x['SPA_DIR'] == x['lane_direction'] if x['lane_direction'] != 'Both' else True, axis=1)]
    return matcheddirection

# Run the new fields and filtering process
newfield_df = make_newfields(df)
filter_df = filteronlymatching(newfield_df)

''' Part 3: Dissolve the muliple joined values for each stop into one, then write results to the original stop database'''

def unique_values_by_id(df, idcolumn, valuescolumn): # Take a many to one join and return unique join values
    unique_dict = {}
    for row in df[[idcolumn,valuescolumn]].to_dict('records'):
        key = row[idcolumn]
        value = row[valuescolumn]
        if key not in unique_dict.keys():
            unique_dict[key] = [value]
        else:
            if value not in unique_dict[key]:
                unique_dict[key].append(value)
    return unique_dict

def dissolve_many_join(df, join_id, groupfields, mergefields): # Take a many to one join, dissolve, and merge fields
    # Create a dictionary for every field you want merged
    mergefielddicts = []
    for m in mergefields:
        merged = unique_values_by_id(df, join_id, m)
        mergefielddicts.append(merged)
    # Do a group by. Get only unique stop IDs for each route name, bus lane, and bus lane street, to get rid of repeats
    stopids = df.groupby(groupfields).size().reset_index()
    # Make a new dataframe
    dfconstruct = []
    for row in stopids.to_dict('records'):
        newrow = {}
        fid = row[join_id]
        for g in groupfields: # Append group values to row
            newrow[g] = row[g]
        for j, mdict in enumerate(mergefielddicts): # Append the unique values to row
            newrow[mergefields[j]] = mdict[fid]
        dfconstruct.append(newrow)
    return pd.DataFrame(dfconstruct)

# Run the dissolve process
groupfields = ['TARGET_FID','stop_id','route_name','facility','street']
mergefields = ['segmentid']
tojoin_df = dissolve_many_join(filter_df,'TARGET_FID', groupfields, mergefields)

# Create new "joined" feature class 
newjoined_fc = r'C:\Users\1280530\GIS\Bus Lanes\01_Data\Bus_Lanes.gdb\Stops_In_Lanes_202206'
arcpy.management.CopyFeatures(bus_stops, newjoined_fc)

def addfcfields(fc_path, newfields):
    existing = [f.name for f in arcpy.ListFields(fc_path) if f.name != 'OBJECTID']
    existingcols = ['OID@'] + existing
    # Check that new fields don't already exist
    fieldstoadd = [[n, 'TEXT', n, 1000, ''] for n in newfields if n not in existingcols]
    # Add new fields 
    if len(fieldstoadd) > 0:
        arcpy.management.AddFields(fc_path, fieldstoadd)

# Add fields
joinfields = ['OID@','facility','street','segmentid']
addfcfields(newjoined_fc, joinfields)

# Write values into a dictionary
def to_dict2(df, indexfield):
    return df.groupby(indexfield).first().to_dict('index')

joindict = to_dict2(tojoin_df, 'TARGET_FID')

# Join the spatial join values to the new feature class
with arcpy.da.UpdateCursor(newjoined_fc,joinfields) as cursor:
    for row in cursor:
        fid = row[0]
        if fid in joindict.keys():
            row[1] = joindict[fid]['facility']
            row[2] = joindict[fid]['street']
            row[3] = ' '.join([str(x) for x in joindict[fid]['segmentid']])
        cursor.updateRow(row)
