import pandas as pd
from urllib import quote


nyc_path = 'https://data.cityofnewyork.us/resource/ry4b-kref.json'

all_data = pd.read_json(nyc_path)

all_roads = pd.Series(all_data['roadway_names'])
all_roads.append(all_data['to'])
all_roads.append(all_data['from'])

unique_roads = all_roads.unique()

defined_roads = all_data[['roadway_name', 'direction']]
defined_roads.drop_duplicates()

class Intersection:
    def __init__(self, identity, roads):
        self.roads = roads
        self.identity = identity

    def contains_road(self, road):
        if self.roads.count(road) > 0:
            return True
        return False

    def road_identities(self):
        return [self.roads[0].identity, self.roads[1].identity]

    def contains_name(self, name):
        for segment in self.roads:
            if segment.name == name:
                return True
        return False

    def contains_id(self, identity):
        for segment in self.roads:
            if segment.identity == identity:
                return True
        return False

class Segment:
    def __init__(self, identity, road, direction):
        self.identity = identity
        self.name = road
        self.direction = direction

class Map:
    def __init__(self):
        self.intersections = []
        self.roads = []

    def road_intersections(self, identity):
        inters = []
        for inter in self.intersections:
            if inter.contains_id(identity):
                inters.append(inter)
        return inters

    def has_road(self, name, direction):
        for segment in self.roads:
            if segment.name == name and segment.direction == direction:
                return True
        return False

    def has_intersection(self, id1, id2):
        for inter in self.intersections:
            ids = inter.road_identities()
            if ids.count(id1) > 0 and ids.count(id2) > 0:
                return True
        return False

    def create_road(self, name, direction):
        if self.has_road(name, direction):
            return
        identity = len(self.roads)
        road = Segment(identity, name, direction)
        self.roads.append(road)

    def create_intersection(self, identities):
        id1, id2 = identities
        if self.has_intersection(id1,id2):
            return
        segs = [self.roads[id1], self.roads[id2]]
        inter = Intersection(len(self.intersections), segs)
        self.intersections.append(inter)

