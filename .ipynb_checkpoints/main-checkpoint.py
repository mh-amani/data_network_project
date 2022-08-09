from class_network import *

network = Network(4, 3, [(1, 1), (2, 1), (1, 2), (2, 2)])
network.init_network()

network.add_user(0, [(0, 0), (0, 2)], [0.5], [0.1, 0.8, 0.5, 0.5])
network.add_user(1, [(3, 0), (3, 2)], [1], 0)
network.add_user(2, [(1, 0), (0, 1), (3, 2)], [0.5, 2], [0.1, 0.7, 0.3, 0.4])
# network.connection_request(0, 1, '1.txt')
network.connection_request(2, 3, '2.txt')

network.run()
