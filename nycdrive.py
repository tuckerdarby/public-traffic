import pandas as pd
from math import sqrt


#Node - aka intersection
class Node:
    def __init__(self, npk, spks):
        self.npk = npk
        self.spks = spks
        self.edges = []
        self.epks = []
        self.locs = []

    def add_edge(self, epk, edge):
        if self.epks.count(epk) == 0:
            self.edges.append(edge)
            self.epks.append(epk)


#Edge - aka segment
class Edge:
    def __init__(self, epk, to_node, from_npk, weight_data):
        self.epk = epk
        self.to_node = to_node
        self.from_npk = from_npk
        self.weight_data = weight_data

    def get_cost(self, time):
        cost = self.weight_data[time].sum()
        return cost


#Map - aka graph
class Map:
    def __init__(self):
        #holds actual objects
        self.streets = {}
        self.edges = []
        self.nodes = []

    #streets is just a marker for a name of a street to an id used to check if nodes are similar
    def register_street(self, street_name):
        street_name = format_name(street_name)
        if self.streets.has_key(street_name):
            print ('Street already registered')
            return
        street_count = len(self.streets)
        self.streets[street_name] = street_count
        return street_count

    #get street name
    def get_street_name(self, sid):
        for key, spk in self.streets.iteritems():
            if sid == spk:
                return key

    #get street id by street name
    def get_street_pk(self, street_name):
        street_name = format_name(street_name)
        if not self.streets.has_key(street_name):
            return -1
        return self.streets[street_name]

    #get node id by street ids
    def get_node_pk(self, spk1, spk2):
        for node in self.nodes:
            chks = node.spks
            if chks.count(spk1) > 0 and chks.count(spk2) > 0:
                return node.npk
        return -1

    #get node object by names
    def get_intersection_node(self, street_names):
        street_names[0] = format_name(street_names[0])
        street_names[1] = format_name(street_names[1])
        spk1 = self.get_street_pk(street_names[0])
        spk2 = self.get_street_pk(street_names[1])
        npki = self.get_node_pk(spk1, spk2)
        if npki == -1:
            return -1
        return self.nodes[npki]

    #create node from intersection names
    def create_node(self, street1_name, street2_name, locs):
        spk1 = self.get_street_pk(street1_name)
        spk2 = self.get_street_pk(street2_name)
        if spk1 == -1 or spk2 == -1:
            print ('Unregistered street')
            return [spk1, spk2]
        npk = self.get_node_pk(spk1, spk2)
        if npk != -1:
            print ('Previously registered intersection')
            return npk
        npk = len(self.nodes)
        node = Node(npk, [spk1, spk2])
        node.locs = locs
        self.nodes.append(node)
        return npk

    #get edge ID from two node IDs
    def get_edge_pk(self, to_npk, from_npk):
        for edge in self.edges:
            e_to_npk = edge.to_node.npk
            e_from_npk = edge.from_npk
            if e_to_npk == to_npk and e_from_npk == from_npk:
                return edge.epk
        return -1

    #create edge using three names that should have already been used to make two nodes
    def create_edge(self, mid_name, to_name, from_name, weight_df=None):
        mid_spk = self.get_street_pk(mid_name)
        to_spk = self.get_street_pk(to_name)
        from_spk = self.get_street_pk(from_name)
        if mid_spk == -1 or to_name == -1 or from_name == -1:
            print('Edge Error: unregistered street(s)', mid_name, mid_spk, to_name, to_spk, from_name, from_spk)
            return -1
        from_npk = self.get_node_pk(mid_spk, from_spk)
        to_npk = self.get_node_pk(to_spk, mid_spk)
        if from_npk == -1 or to_npk == -1:
            print('Edge error: unregistered node(s)', mid_name, to_name, from_name)
            return -1
        epk = self.get_edge_pk(to_npk, from_npk)
        if epk != -1:
            print('Error: previously registered edge', epk, mid_name, to_name, from_name)
            return -1
        epk = len(self.edges)
        edge = Edge(epk, self.nodes[to_npk], from_npk, weight_df)
        self.edges.append(edge)
        self.nodes[from_npk].add_edge(epk, edge)
        return epk


class Traveller:
    def __init__(self, start_node, end_node, work_hour):
        self.start = start_node
        self.visited = [start_node]
        self.goal = end_node
        self.time = work_hour
        self.path = []
        self.travelled = 0

    def dfs_travel(self):
        self.dfs_search(self.visited, [self.start.npk])

    def dfs_search(self, route, node_pks):
        current_i = len(route) - 1
        current_node = route[current_i]
        if current_node == self.goal:
            curr_path = len(self.path)
            if curr_path == 0:
                self.path = route
            elif len(route) < curr_path:
                self.path = route
        for edge in current_node.edges:
            if node_pks.count(edge.to_node.npk) == 0:
                go_node = edge.to_node
                route2 = []
                route2.extend(route)
                route2.append(go_node)
                node_pks2 = []
                node_pks2.extend(node_pks)
                node_pks2.append(go_node.npk)
                self.dfs_search(route2, node_pks2)

    def greedy_travel(self):
        self.greedy_search(self.visited, [self.start.npk], 0)

    def greedy_search(self, route, node_pks, curr_cost):
        current_i = len(route) - 1
        current_node = route[current_i]
        if current_node == self.goal:
            curr_path = len(self.path)
            if curr_path == 0 or len(route) < curr_path:
                self.path = route
                self.travelled = curr_cost
        min_cost = 999999
        go_node = None
        locs1 = current_node.locs
        for edge in current_node.edges:
            if node_pks.count(edge.to_node.npk) == 0:
                locs2 = edge.to_node.locs
                cost = get_distance(locs1, locs2)
                if cost < min_cost:
                    min_cost = cost
                    go_node = edge.to_node
        if go_node is not None:
            now_cost = curr_cost + cost
            route2 = []
            route2.extend(route)
            route2.append(go_node)
            node_pks2 = []
            node_pks2.extend(node_pks)
            node_pks2.append(go_node.npk)
            self.greedy_search(route2, node_pks2, now_cost)


def get_distance(loc1, loc2):
    x1, y1 = loc1
    x2, y2 = loc2
    dx = abs(x2-x1)
    dy = abs(y2-y1)
    dist = sqrt(dx*dx+dy*dy)
    return dist

#the formats between the two databases are different - this fixes that
def format_name(title):
    title = str(title).strip()
    title = str(title).upper()
    title = title.replace('STREET', 'ST')
    title = title.replace('AVENUE', 'AVE')
    title = title.replace('WEST', 'W')
    title = title.replace('EAST', 'E')
    title = title.replace('SOUTH', 'S')
    title = title.replace('NORTH', 'N')
    title = title.replace('PARKWAY', 'PKWY')
    title = title.replace('PLACE', 'PL')
    for check_i in range(10):
        title = title.replace(str(check_i) + 'RD', str(check_i))
        title = title.replace(str(check_i) + 'ND', str(check_i))
        title = title.replace(str(check_i) + 'ST', str(check_i))
        title = title.replace(str(check_i) + 'TH', str(check_i))
    return title


nyc_map = Map()
congestion_map = False
geolocation_map = True

if congestion_map:
    #nyc traffic data
    nyc_path = 'https://data.cityofnewyork.us/resource/ry4b-kref.json'
    all_data = pd.read_json(nyc_path).drop_duplicates()
    road_tos = all_data['to'].drop_duplicates()
    road_froms = all_data['from'].drop_duplicates()
    road_cents = all_data['roadway_name'].drop_duplicates()
    all_roads = road_cents.append(road_froms).append(road_tos).unique()

    #register streets - non unique to direction
    for reg_road in all_roads:
        nyc_map.register_street(str(reg_road).strip())

    #create nodes
    roadway_df = all_data[['roadway_name', 'to', 'from']].drop_duplicates()
    for roadway_line in roadway_df.iterrows():
        road_mid = roadway_line[1]['roadway_name']
        road_to = roadway_line[1]['to']
        road_from = roadway_line[1]['from']
        fr_nd = nyc_map.create_node(str(road_mid).strip(), str(road_from).strip())
        to_nd = nyc_map.create_node(str(road_to).strip(), str(road_mid).strip())

    #create edges and weights
    for row in roadway_df.iterrows():
        edg_mid = str(row[1]['roadway_name']).strip()
        edg_to = str(row[1]['to']).strip()
        edg_from = str(row[1]['from']).strip()
        weight_dfs = all_data.where(all_data['to'] == edg_to)\
            .where(all_data['from'] == edg_from).where(all_data['roadway_name'] == edg_mid).dropna()\
            .drop(['to', 'from', 'roadway_name', 'segment_id', 'id', 'direction'], 1)
        edge_pk = nyc_map.create_edge(edg_mid, edg_to, edg_from)
        edger_pk = nyc_map.create_edge(edg_mid, edg_from, edg_to)

#nyc geolocation data
if geolocation_map:
    geo_path = 'https://gist.githubusercontent.com/rshipp/537bdf57008cdc02227c1e80771574c7/raw/697fd1ea2248a768c0814ba28569f2eeef549555/coordinates.json'
    geo_data = pd.read_json(geo_path)

    #geo streets and nodes
    road_ones = []
    road_twos = []
    for geo_roads in geo_data.iterrows():
        if len(geo_roads[1][0]) < 2:
            continue
        gx, gy = geo_roads[1][0]
        rx, ry = geo_roads[0].split(',')
        rx = format_name(rx)
        ry = format_name(ry)
        gx = float(gx)
        gy = float(gy)
        nyc_map.register_street(rx)
        nyc_map.register_street(ry)
        nyc_map.create_node(rx, ry, [gx, gy])
        road_ones.append(rx)
        road_twos.append(ry)
    r_i = len(road_ones) - 1

    #geo edges
    while r_i > 0:
        r2 = r_i - 1
        if road_ones[r_i] == road_ones[r2]:
            rn_mid = road_ones[r_i]
            rn_to = road_twos[r_i]
            rn_from = road_twos[r2]
            nyc_map.create_edge(rn_mid, rn_to, rn_from)
            nyc_map.create_edge(rn_mid, rn_from, rn_to)
        r_i -= 1


#Finished building graph
print ('Total nodes:', len(nyc_map.nodes))

#Example - unconnected
inter1 = ['STAFFORD AVE', 'HUGUENOT AVE']
inter2 = ['AVE T', 'CONEY ISLAND AVE']

inter_node1 = nyc_map.get_intersection_node(inter1)
inter_node2 = nyc_map.get_intersection_node(inter2)

max_nodes = len(nyc_map.nodes)

car = Traveller(inter_node1, inter_node2, 'NA')
car.dfs_travel()
print car.path
#test all potential paths
printed = False
catch_path = []
if True:
    for i in range(max_nodes):
        for n in range(max_nodes):
            if i == n:
                continue
            node_i = nyc_map.nodes[i]
            node_n = nyc_map.nodes[n]
            car = Traveller(node_i, node_n, '_9_00_10_00pm')
            if geolocation_map and not congestion_map:
                car.greedy_travel()
            else:
                car.dfs_travel()
            if len(car.path) > 7:# printed:
                printed = True
                catch_path = car.path

for pth in catch_path:
    fspk1, fspk2 = pth.spks
    sname1 = nyc_map.get_street_name(fspk1)
    sname2 = nyc_map.get_street_name(fspk2)
    print (sname1, sname2)

