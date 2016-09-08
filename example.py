from nycdrive import *

#Example - unconnected
inter1 = ['STAFFORD AVE', 'HUGUENOT AVE']
inter2 = ['AVE T', 'CONEY ISLAND AVE']

inter_node1 = nyc_map.get_intersection_node(inter1)
inter_node2 = nyc_map.get_intersection_node(inter2)

max_nodes = len(nyc_map.nodes)

car = Traveller(inter_node1, inter_node2, 'NA')
car.dfs_travel()
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
