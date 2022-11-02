# Bus stop to routes join
import arcpy 
import pandas as pd

# Define the bus lane segment fc and bus stops fc
env = r'C:\Users\1280530\GIS\Bus Lanes\01_Data\Bus_Lanes.gdb\\'
lane_segments = env + r'Bus_Lanes_Segments'
bus_stops = env + r'stops_2207_model'

# Define the fields we want joined
tojoinfields = ['street','segmentid','facility', 'hours','routes_ser', 'routes_nod']

# Define spatial join output
spatialjoin_fc = env + r'stops_lanes_manyjoin2207_1102'

# Define route id and direction field
route_id_field = 'gtfs_route_id'
dir_id_field = 'direction_id' 

# Define group fields and merge fields

# Define add fields and merge fields

# Define new output feature class
newjoined_fc = r'C:\Users\1280530\GIS\Bus Lanes\01_Data\Bus_Lanes.gdb\Stops_In_Lanes_202207_1102'

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
    joinListFields = [f.name for f in arcpy.ListFields(rightfc)]
    print('Full fields list: ', joinListFields)
    missing = [n for n in rightfieldstojoin if n not in joinListFields]
    if len(missing) > 0:
        print('The following fields are not in the join feature class: ', missing)
        return False
    else:
        # Add the fields we want joined to field mapping object
        print('Fields to join: ', rightfieldstojoin)
        for fname in rightfieldstojoin:
            fieldmappings.addFieldMap(make_field_map(lane_segments, fname))
        return fieldmappings

def runspatialjoin(leftfc, rightfc, rightfieldstojoin, outfc):
    fieldmappings = makefieldmappings(leftfc, rightfc, rightfieldstojoin)
    if fieldmappings == False:
        print('Please correct fields you want joined.')
    else:
        arcpy.analysis.SpatialJoin(bus_stops, lane_segments, outfc, join_operation='JOIN_ONE_TO_MANY',join_type='KEEP_COMMON',field_mapping=fieldmappings,
        match_option='WITHIN_A_DISTANCE',search_radius='80 FEET')

# Run the spatial join
if arcpy.Exists(spatialjoin_fc) == False:
    runspatialjoin(bus_stops, lane_segments, tojoinfields, spatialjoin_fc)
    print('New spatial join feature class created as: ', spatialjoin_fc)

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

def returndirection(value): # Return a direction from a string
    directions = {'(NB)':'NB','(SB)':'SB','(EB)':'EB','(WB)':'WB'}
    matches = []
    for d in directions.keys():
        if d in value:
            matches.append(directions[d])
    if len(matches)==1:
        return matches[0]
    elif len(matches)==0:
        return 'Both'
    else:
        return 'Flag'

def make_newfields(df, routeid, routedir): # Make route name, lane direction, and routes list fields
    req_fields = ['routes_ser','facility']
    missing = [r for r in req_fields if r not in df.columns]
    if len(missing) > 0:
        print('The following required fields are missing: ', missing)
    # Filter out stop IDs that weren't joined to a bus lane that serves routes
    join_df = df.loc[df['routes_ser'] == df['routes_ser']].copy()
    # Create route + direction field called 'route_name'
    join_df['route_name'] = join_df.apply(lambda x: str(x[routeid]) + ' ' + str(x[routedir]), axis=1)
    # Find the direction of the bus lane
    join_df['lane_direction'] = join_df.loc[:,'facility'].apply(lambda x: returndirection(x))
    # Split routes_served into a list
    join_df['routes_list'] = join_df.loc[:,'routes_ser'].apply(lambda x: x.split(';'))
    return join_df

def dir_validation(in_dir, comp_dir):
    if in_dir == comp_dir:
        return True
    elif comp_dir == 'Both':
        return True
    elif in_dir != comp_dir and in_dir in ['EB','WB'] and comp_dir in ['EB','WB']:
        return False
    elif in_dir != comp_dir and in_dir in ['NB','SB'] and comp_dir in ['NB','SB']:
        return False
    else:
        return 'Flag'

def filteronlymatching(df): # Make sure only matching route and direction fields are included
    # Check to make sure the bus stop's route_name matches the list of routes that bus lane serves
    matchedroute = df[df.apply(lambda x: x['route_name'] in x['routes_ser'], axis = 1)].copy()
    # Check to make sure the stop's SPA_DIR matches the bus lane direction
    matchedroute['dir_valid'] = matchedroute.apply(lambda x: dir_validation(x['SPA_DIR'], x['lane_direction']), axis=1)
    matcheddirection = matchedroute.loc[(matchedroute['dir_valid'] == True) | (matchedroute['dir_valid'] == 'Flag')].copy()
    # Return direction mismatch flag instead
    print('Original: ', len(df), ' ','Filtered: ', len(matcheddirection))
    return matcheddirection

# Run the fc to dataframe script
df = fc_to_df(spatialjoin_fc)
print(df.columns)

# Run the new fields and filtering process
newfield_df = make_newfields(df, route_id_field, dir_id_field)
filter_df = filteronlymatching(newfield_df)

''' Part 3: Dissolve the muliple joined values for each stop into one'''

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

def dissolve_many_join(df, join_id, groupfields, mergefields): # Take a one-to-many join, dissolve, and merge fields
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
groupfields = ['TARGET_FID','STO_BOX_ID','route_name','facility','street','dir_valid']
mergefields = ['facility','street','segmentid']
tojoin_df = dissolve_many_join(filter_df,'TARGET_FID', groupfields, mergefields)

'''Part 4: Make a copy of the original stop fc, then write join data to it'''

def addfcfields(fc_path, newfields, length):
    existing = [f.name for f in arcpy.ListFields(fc_path) if f.name != 'OBJECTID']
    existingcols = ['OID@'] + existing
    # Check that new fields don't already exist
    fieldstoadd = [[n, 'TEXT', n, length, ''] for n in newfields if n not in existingcols]
    # Add new fields 
    if len(fieldstoadd) > 0:
        arcpy.management.AddFields(fc_path, fieldstoadd)

def to_dict2(df, indexfield):
    return df.groupby(indexfield).first().to_dict('index')

def write_new_field_data_tofc(fc_path, df, join_id, newdata, newdata_merge):
    # Add new fields to feature class if they don't exist
    addfcfields(fc_path, newdata,255)
    addfcfields(fc_path, newdata_merge, 1000)
    # Convert new data to dictionary
    joindict = to_dict2(df,join_id)
    # Join the spatial join values to the new feature class
    newdata2 = ['OID@'] + newdata
    with arcpy.da.UpdateCursor(fc_path, newdata2) as cursor:
        for row in cursor:
            fid = row[0]
            if fid in joindict.keys():
                for i, ndata in enumerate(newdata2):
                    if i != 0:
                        row[i] = joindict[fid][ndata]
            cursor.updateRow(row)
    newdata_merge2 = ['OID@'] + newdata_merge
    # Add segment id
    with arcpy.da.UpdateCursor(fc_path, newdata_merge2) as cursor:
        for row in cursor:
            fid = row[0]
            if fid in joindict.keys():
                for i, ndata in enumerate(newdata_merge2):
                    if i != 0:
                        segmentidlist = joindict[fid][ndata]
                        row[i] = ', '.join([str(x) for x in segmentidlist])
            cursor.updateRow(row)
            
# Create a copy of the original stop fc
if arcpy.Exists(newjoined_fc) == False:
    arcpy.management.CopyFeatures(bus_stops, newjoined_fc)
    print('New stops feature class created as: ', newjoined_fc)

# Define add fields
ndata = ['dir_valid']
ndata_merge = ['facility','street','segmentid']
# Run the write data function
write_new_field_data_tofc(newjoined_fc, tojoin_df, 'TARGET_FID', ndata, ndata_merge)
