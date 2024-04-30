"""This profile create lan that spans two clusters. Note that you must a bandwidth on your lan for this to work.

Instructions:
Click on any node in the topology and choose the `shell` menu item. When your shell window appears, use `ping` to test the link."""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Variable number of nodes at two sites.
pc.defineParameter("X", "Number of Nodes at Site One", portal.ParameterType.INTEGER, 2)
pc.defineParameter("Y", "Number of Nodes at Site Two", portal.ParameterType.INTEGER, 2)
pc.defineParameter("phystype1",  "Optional physical node type for cluster1",
                   portal.ParameterType.STRING, "",
                   longDescription="Specify a single physical node type (pc3000,d710,etc) " +
                   "instead of letting the resource mapper choose for you.")
pc.defineParameter("phystype2",  "Optional physical node type for cluster2",
                   portal.ParameterType.STRING, "",
                   longDescription="Specify a single physical node type (pc3000,d710,etc) " +
                   "instead of letting the resource mapper choose for you.")

# Retrieve the values the user specifies during instantiation.
params = pc.bindParameters()

# Check parameter validity.
if params.X < 2:
    pc.reportError(portal.ParameterError("You must choose at least 2 nodes at Site One"))
if params.Y < 2:
    pc.reportError(portal.ParameterError("You must choose at least 2 nodes at Site Two"))

# Count for node name.
counter = 0;

# ifaces. 
ifaces = []

# Nodes at Site One.
for i in range(params.X):
    node = request.RawPC("node" + str(counter))
    # Assign to Site One.
    node.Site("Site1")
    node.hardware_type = params.phystype1
    # Create iface and assign IP
    iface = node.addInterface("eth1")
    # Specify the IPv4 address
    iface.addAddress(pg.IPv4Address("10.10.1." + str(counter + 1), "255.255.255.0"))
    ifaces.append(iface)
    counter = counter + 1
    pass

# Nodes at Site Two
for i in range(params.Y):
    node = request.RawPC("node" + str(counter))
    # Assign to Site Two
    node.Site("Site2")
    node.hardware_type = params.phystype2
    # Create iface and assign IP
    iface = node.addInterface("eth1")
    # Specify the IPv4 address
    iface.addAddress(pg.IPv4Address("10.10.1." + str(counter + 1), "255.255.255.0"))
    # And add to the lan.
    ifaces.append(iface)
    counter = counter + 1
    pass

# Now add the link to the rspec. 
lan = request.LAN()

# Must provide a bandwidth. BW is in Kbps
lan.bandwidth = 100000

# Add interfaces to lan
for iface in ifaces:
    lan.addInterface(iface)

# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)