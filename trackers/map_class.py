

from numpy import absolute


class MapObject:
    def __init__(self,
                 name="",
                 source="",
                 geo="",
                 fuel="",
                 pm="",
                 data=[],
                 about="",
                 dep_abouts=[]
                 ):
        self.name = name
        self.source = source.split(", ")
        self.geo = geo
        self.fuel = fuel.split(", ")
        self.pm = pm.split("; ")
        self.data = data
        self.about = about
        self.dep_abouts = dep_abouts
    
    
    # def getSourceData(self):
    #     # using source attribute which is a list of tracker names per map
    #     # go into source tab
    #     # use the tracker name as look up for the acro, key, tabs, release date
    #     # double check release date
    #     # create df 
    #     df_list = []
    #     for item in self.source:
    #             print(f'Processing source item: {item}')
    #             # create object or df 
    #             data = create_df_from_source(item)
    #             df_list.append(data)
    #     df = ''
    #     return df
    # TODO look into getter and setter methods
    # If you're changing any information in the object DO it via a method in the object 
    
    def filter_by_fuel(self):
        
        # using fuel attribute, which often times will be none, filter out rows in df
        if self.fuel == 'none':
            pass
        else:
            print(f'filter by fuel: {self.fuel}')
            
    def filter_by_geo(self):
        
        # using geo attribute, find country/area column and use gem list 
        # to filter out countries not in map's region
        if self.geo == 'global':
            pass
        else:
            print(f'filter by geo: {self.geo}')
        