from pyvis.network import Network

# Step 1: Create a Pyvis network object
net = Network(height='600px', width='100%', directed=False)

# Add nodes (entities)
net.add_node("Alice", title="Alice")
net.add_node("Bob", title="Bob")
net.add_node("Charlie", title="Charlie")
net.add_node("David", title="David")

# Add edges (relationships) with labels and some customization
net.add_edge("Alice", "Bob", label="friend", font=dict(size=20, color="blue"))
# net.add_edge("Alice", "Charlie", label="colleague", font=dict(size=20, color="green"))
net.add_edge("Bob", "David", label="friend", font=dict(size=20, color="red"))
net.add_edge("Charlie", "David", label="colleague", font=dict(size=20, color="purple"))

# Generate the interactive HTML file
net.save_graph("entity_relationship_graph_with_custom_labels.html")
