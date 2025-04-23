
tracker_summary_pages = {
    "Oil and Gas Plants": [
        "Oil and Gas Plants by Country/Area (MW)",
        "Oil and Gas Plants by Country/Area (Power Stations)",
        "Oil and Gas Plants by Country/Area (Units)",
        "Oil and Gas Plants by Region (MW)",
        "Ownership of Oil and Gas Plants in Africa (MW)",
        "Oil and Gas Plants by Technology by Country/Area (MW)"
    ],
    "Coal Plants": [
        "Coal Plants by Country/Area (MW)",
        "Coal Plants by Country/Area (Power Stations)",
        "Coal Plants by Country/Area (Units)",
        "Coal Plants by Region (MW)"
    ],
    "Geothermal": [
        "Geothermal Power Capacity by Country/Area (MW)",
        "Geothermal Unit Count by Country/Area",
        "Geothermal Power Capacity by Installation Type and Region (MW)",
        "Geothermal Operational Capacity Installed by Country/Area and Year (MW)",
        "Geothermal Prospective Capacity by Country/Area and Year (MW)"
    ],
    "Bioenergy": [
        "Bioenergy Capacity by Country/Area (MW)",
        "Bioenergy Unit Count by Country/Area",
        "Bioenergy Fuel Types by Country/Area",
        "Bioenergy Capacity by Region (MW)",
        "Bioenergy Unit Count by Region",
        "Bioenergy Fuel Types by Region",
        "Bioenergy Operational Capacity Added by Country/Area and Year (MW)"
    ],
    "Wind": [
        "Wind Farm Capacity by Country/Area (MW)",
        "Wind Farm Phase Count by Country/Area",
        "Wind Farm Capacity by Region (MW)",
        "Wind Farm Phase Count by Region",
        "Wind Farm Capacity by Installation Type and Region (MW)",
        "Wind Farm Operational Capacity by Country/Area and Year (MW)",
        "Wind Farm Prospective Capacity by Country/Area and Year (MW)"
    ],
    "Solar": [
        "Solar Farm Capacity by Country/Area (MW)",
        "Solar Farm Phase Count by Country/Area",
        "Solar Farm Capacity by Region (MW)",
        "Solar Farm Phase Count by Region",
        "Solar Farm Operational Capacity by Country/Area and Year (MW)",
        "Solar Farm Prospective Capacity by Country/Area and Year (MW)"
    ],
    "Hydropower": [
        "Hydropower Capacity by Country/Area (MW)",
        "Hydropower Project Count by Country/Area",
        "Hydropower Capacity by Region and Subregion (MW)",
        "Hydropower Project Count by Region and Subregion",
        "Hydropower Capacity by Region and Type (MW)"
    ],
    "Nuclear": [
        "Nuclear Power Capacity by Country/Area (MW)",
        "Nuclear power Unit Count by Country/Area",
        "Nuclear Power Capacity by Region and Subregion (MW)",
        "Nuclear Power Unit Count by Region and Subregion",
        "Nuclear Power Capacity by Reactor Type and Region (MW)"
    ],
    "Oil & Gas Pipelines": [
        "Gas Pipeline Length by Country/Area (km)",
        "Gas Pipeline Length by Region (km)",
        "Oil Pipeline Length by Country/Area (km)",
        "Oil Pipeline Length by Region (km)"
    ],
    "LNG Terminals": [
        "LNG Export Projects by Region",
        "LNG Export Projects by Country/Area",
        "LNG Import Projects by Region",
        "LNG Import Projects by Country/Area",
        "LNG Export Capacity by Region (mtpa)",
        "LNG Export Capacity by Country/Area (mtpa)",
        "LNG Import Capacity by Region (mtpa)",
        "LNG Import Capacity by Country/Area (mtpa)",
        "LNG Terminals by Start Year",
        "LNG Capacity by Start Year (mtpa)"
    ],
    "Coal Terminals": [
        "Number of Coal Terminals by Country/Area",
        "Coal Terminal Capacity by Country/Area",
        "Coal Terminal Capacity by Region",
        "Coal Terminal Capacity by Type (Import/Export)"
    ],
    "Oil & Gas Extraction": [
        "Oil & Gas Extraction Sites by Region",
        "Oil & Gas Extraction Sites by Country/Area",
        "Oil Production by Sub Region",
        "Oil Production by Country/Area",
        "Gas Production by Region",
        "Gas Production by Country/Area"
    ],
    "Coal Mines": [
        "Number of Coal Mines by Country/Area"
    ]
}


#########################
### SUMMARY FILES ###
#########################

# # TODO maybe do this once it is one_gdf so we have consistent column names
# def create_summary_files(dict_list_dfs): # map name: list of filtered dfs for map
#     # go through each df
#     types_of_pivots = {'all': ['Country', 'Owner', 'Start year', 'Province']} # come back to this, can be {tracker name: [list of specific pivot types]}
#     cols_to_organize = ['Status', 'Start year']
#     cols_to_sum = ['Capacity', 'Kilometers']
#     cols_to_count = ['Project Name']
#     status_filter = ['operating', 'prospective']
#     country_filter = ['China']
    
#     dict_of_summary_dfs = {} # {mapname: [list of summary dfs]}
#     list_of_summary_dfs = []
#     for mapname, list_dfs in dict_list_dfs.items():
#         for df in list_dfs:
#             # have a list of all files needed
#             # do a groupby to create the df for each file
#             df = df.reset_index(drop=True)
#             # # printf'this is df cols: {df.cols}') # yep it was reset issue, just needs consistnet column names no Country
#             tracker = df['tracker-acro'].loc[0]
#             # # printf'Creating summary files for {tracker}')
#             for pivot_type in types_of_pivots['all']:
#                 pivot = df.groupby([pivot_type, 'Status'])['Capacity'].sum().reset_index() 
#                 list_of_summary_dfs.append(pivot)
#     dict_of_summary_dfs[mapname] = list_of_summary_dfs
#     # TODO save each df to a gsheet and or excel
#     df = pd.DataFrame(dict_of_summary_dfs)
#     sheet = gspread_creds.open("https://docs.google.com/spreadsheets/d/18zyOMB7S_bAnvFDOPqC1emPA_AT1OMO26CXzTjpwN7o/edit?gid=0#gid=0").sheet1  # Use .worksheet("Sheet Name") to specify a sheet
#     set_with_dataframe(sheet, df)
    
#     return None

# def pull_existing_summary_files(prep_df):
#     # in prep_df get the URL for each tracker's summary tables
#     # using scrapy or bs go to the site and find each summary table by the div
#     # pull the google link 
#     # read the google link into df with gspread
#     # pull the title
#     # compare title to the needed ones for AET
#     # if in their pull it and filter for Africa so we can compare to the new one
#     # we can compare manually for now
#     return None