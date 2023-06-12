import Pyro5.api

# Define the available states
STATES = {'INICIADOR', 'OCIOSO', 'VISITADO', 'OK'}

# Define the initial states
SINI = {'INICIADOR', 'OCIOSO'}

# Define the terminal states
STERM = {'OK'}

# Define the constraints
RESTRICTIONS = {'CN', 'TR', 'BL', 'UI'}

# Pyro5 configuration
Pyro5.config.SERIALIZERS_ACCEPTED.add('pickle')
Pyro5.config.SERIALIZER = 'pickle'


class Node:
    def __init__(self):
        self.state = 'INICIADOR'
        self.not_visited = set()
        self.is_initiator = False
        self.input_source = None

    def spontaneously(self):
        self.not_visited = self.get_not_visited()
        self.is_initiator = True
        self.visita()

    def recebe_T(self, origem):
        self.input_source = origem
        self.not_visited = self.get_not_visited() - {origem}
        self.is_initiator = False
        self.visita()

    def recebe_R(self):
        self.visita()

    def recebe_B(self):
        self.visita()

    def visita(self):
        if self.not_visited:
            prox = self.not_visited.pop()
            self.state = 'VISITADO'
            self.envia_T(prox)
        else:
            self.state = 'OK'
            if not self.is_initiator:
                self.envia_R(self.input_source)

    def envia_T(self, prox):
        with Pyro5.api.Proxy("PYRONAME:node.{}".format(prox)) as remote_node:
            remote_node.recebe_T(Pyro5.api.current_context.addr)

    def envia_R(self, origem):
        with Pyro5.api.Proxy("PYRONAME:node.{}".format(origem)) as remote_node:
            remote_node.recebe_R()

    def envia_B(self, origem):
        with Pyro5.api.Proxy("PYRONAME:node.{}".format(origem)) as remote_node:
            remote_node.recebe_B()

    def get_not_visited(self):
        # Implement the logic to retrieve the not visited nodes
        pass


def main():
    # Start the Pyro5 name server
    Pyro5.api.locate_ns()

    # Create a Pyro5 daemon
    daemon = Pyro5.api.Daemon()

    # Register each node with the Pyro5 name server
    for node_name in ['node1', 'node2', 'node3']:
        node = Node()
        with Pyro5.api.Daemon.serveSimple({node: node_name}, host='localhost') as uri:
            print("Registered node {} with URI: {}".format(node_name, uri))

    # Start the main loop
    daemon.requestLoop()


if __name__ == '__main__':
    main()
