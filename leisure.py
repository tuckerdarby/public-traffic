import pandas as pd
import sys


class Street:
    def __init__(self, pk, name):
        self.pk = pk
        self.name = name


class Segment:
    def __init__(self, pk, name, weight, connection):
        #connection should be an id
        self.pk = pk
        self.name = name
        self.weight = weight
        self.node = connection


class Node:
    def __init__(self, pk, segments=[], loc=[]):
        self.pk = pk
        self.edges = segments
        self.location = loc


class Map:
    def __init__(self):
        self.nodes = [] #aka intersections
        self.streets = []
        self.edges = [] #aka edges

    def add_street(self, street_full):
        street_name = street_full.strip()
        pk = len(self.streets)
        for i in range(pk):
            if self.streets[i].name == street_name:
                return
        street = Street(pk, street_name)
        self.streets.append(street)

    def street_pk(self, name):
        for street in self.streets:
            if street.name == name:
                return street.pk

    def intersection_pk(self, pk1, pk2):
        for node in self.nodes:
            if node.edges.count(pk1) > 0 and node.edges.count(pk2) > 0:
                print 'node found:', node, node.pk
                return node.pk
        return -1

    def create_intersection(self, name1, name2, x, y):
        name1 = name1.strip()
        name2 = name2.strip()
        pk1 = self.street_pk(name1)
        pk2 = self.street_pk(name2)
        ipk = self.intersection_pk(pk1, pk2)
        print 'intersection:', ipk
        if ipk == -1:
            ipk = len(self.nodes)
            inter = Node(ipk, [pk1, pk2], [x, y])
            self.nodes.append(inter)
        return ipk

    def create_segment(self, seg, seg_to, seg_from, wpk):
        seg = seg.strip()
        seg_to = seg_to.strip()
        seg_from = seg_from.strip()
        spk = self.street_pk(seg)
        tpk = self.street_pk(seg_to)
        fpk = self.street_pk(seg_from)
        ipk1 = self.intersection_pk(spk, tpk) #to instersection
        ipk2 = self.intersection_pk(spk, fpk) #from intersection
        inter2 = self.nodes[ipk2]
        pk = len(self.edges)
        edge = Segment(pk, seg, wpk, ipk1)
        self.edges.append(edge)
        inter2.edges.append(pk)


class Traveller:
    def __init__(self, road_map, start, end):
        starts = [road_map.street_pk(start[0]), road_map.street_pk(start[1])]
        ends = [road_map.street_pk(end[0]), road_map.street_pk(end[1])]
        self.start = road_map.intersection_pk(starts[0], starts[1])
        #print ('start pk: ', self.start)
        self.end = road_map.intersection_pk(ends[0], ends[1])
        #print ('end pk: ', self.end)
        self.location = self.start
        self.visited = [self.start]
        self.road_map = road_map

    def greedy_search(self):
        cost = 0
        while self.location != self.end:
            options = self.road_map.nodes[self.location].edges
            for loc in self.visited:
                if options.count(loc) > 0:
                    options.remove(loc)
            min_opt = -1
            min_w = sys.maxint
            for option in options:
                w2 = self.road_map.edges[option].weight
                if w2 < min_w:
                    min_w = w2
                    min_opt = option
                if option == self.end:
                    min_opt = option
                    min_w = w2
                    break
            cost += min_w
            self.location = self.road_map.edges[min_opt].connection
            self.visited.append(self.location)
        print ('Trip cost:', cost)


#create basics
nyc_map = Map()
nyc_path = 'https://data.cityofnewyork.us/resource/ry4b-kref.json'
all_data = pd.read_json(nyc_path)
road_tos = all_data['to'].drop_duplicates()
road_froms = all_data['from'].drop_duplicates()
road_cents = all_data['roadway_name'].drop_duplicates()
all_roads = road_cents.append(road_froms).append(road_tos).unique()
for road in all_roads:
    nyc_map.add_street(road)
    print 'adding road', road, nyc_map.streets[len(nyc_map.streets) - 1].pk
#connections
#x1 = all_data[['roadway_name', 'to']].drop_duplicates()
#for r1, r2 in zip(x1['roadway_name'], x1['to']):
#    nyc_map.connect(r1, r2)
#x2 = all_data[['roadway_name', 'from']].drop_duplicates()
#for r3, r4 in zip(x2['roadway_name'], x2['from']):
#    nyc_map.connect(r3, r4)
#weights
#weight_key = '_10_00_11_00am'
#road_weights = all_data[['roadway_name', weight_key]].groupby('roadway_name').sum()
#for r, w in zip(road_weights.index, road_weights[weight_key]):
#    nyc_map.set_weight(r, w)
#load interesections
geo_path = 'https://gist.githubusercontent.com/rshipp/537bdf57008cdc02227c1e80771574c7/raw/697fd1ea2248a768c0814ba28569f2eeef549555/coordinates.json'
inters = pd.read_json(geo_path)
for i in range(len(inters)):
    streets = str(inters.index[i]).split(' , ')
    if len(streets) < 2:
        streets = str(inters.index[i]).split(',')
    if len(streets) < 2:
        streets = str(inters.index[i]).split(', ')
    coords = inters['coordinates'][i]
    if len(coords) == 0:
        print 'NO COORDS'
        continue
    nyc_map.create_intersection(streets[0], streets[1], coords[0], coords[1])
#segments
seg_df = all_data[['roadway_name', 'to', 'from']]
for seg_i in range(len(seg_df)):
    nyc_map.create_segment(seg_df['roadway_name'][i], seg_df['to'][i], seg_df['from'][i], 0)
#travel
start_loc = ['CONEY ISLAND AVE', '']
end_loc = ['FULTON STREET', '']
traveller = Traveller(nyc_map, start_loc, end_loc)
traveller.greedy_search()
print (traveller.visited)