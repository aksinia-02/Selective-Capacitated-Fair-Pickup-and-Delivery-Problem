import networkx as nx
from pyvis.network import Network
import matplotlib.cm as cm
import numpy as np

def get_label(node, nodes_len):

    if node.type == 1:
        label = "depot"
    elif node.type == 2:
        label = f"{node.index}"
    elif node.type == 3:
        label = f"{node.index - 50}"
    else:
        label = str(node.index)
    return label

def display_colored_graph(G, coloring_nodes, edge_coloring, color_map_nodes, color_map_edges, obj_func, output_file="graph.html", show_axes= True):
    """Display the graph with nodes colored based on the assigned coloring_nodes and edges colored based on edge_coloring."""

    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
    customers_len = (len(G.nodes) - 1) / 2

    for node in G.nodes():
        color = coloring_nodes.get(node.index)
        x = node.x
        y = node.y
        net.add_node(
            node.index,
            label=get_label(node,customers_len),
            color=color,
            x=node.x * 50,
            y=node.y * 50,
            #physics=False,
            size=50,
            font={'size': 36, 'face': 'arial', 'vadjust': 0}
        )

    for u, v in G.edges():
        color = edge_coloring.get((u.index, v.index)) or edge_coloring.get((v.index, u.index)) or None
        if color:
            net.add_edge(u.index, v.index, color=color, width=10)

    net.set_options(f"""
    {{
        "nodes": {{
            "font": {{
                "size": 36,
                "face": "arial"
            }}
        }},
        "physics": {{
            "enabled": false
        }},
        "edges": {{
            "smooth": false
        }}
    }}
    """)

    net.show(output_file, notebook=False)

    with open(output_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    legend_html = f"""
    <div style="
        position:absolute;
        top:20px;
        left:20px;
        background-color:white;
        border:2px solid #ccc;
        border-radius:12px;
        padding:14px 18px;
        font-family:Arial, sans-serif;
        font-size:16px;
        box-shadow:0 2px 8px rgba(0,0,0,0.2);
    ">
        <div style="margin-bottom:10px;">
            <div style="display:flex;align-items:center;margin-bottom:6px;">
                <div style="width:18px;height:18px;border-radius:50%;background:{color_map_nodes.get(1)};margin-right:8px;"></div>
                <span>Depot</span>
            </div>
            <div style="display:flex;align-items:center;margin-bottom:6px;">
                <div style="width:18px;height:18px;border-radius:50%;background:{color_map_nodes.get(2)};margin-right:8px;"></div>
                <span>Pickup</span>
            </div>
            <div style="display:flex;align-items:center;">
                <div style="width:18px;height:18px;border-radius:50%;background:{color_map_nodes.get(3)};margin-right:8px;"></div>
                <span>Dropoff</span>
            </div>
        </div>

        <div style="border-top:1px solid #ddd;margin:10px 0;"></div>

        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-weight:regular;color:#333;">Objective:</span>
            <span style="font-weight:bold;color:#763752;">{obj_func:.2f}</span>
        </div>
    </div>
"""

    html_content = html_content.replace("</body>", legend_html + "\n</body>")
    highlight_js = """
        <script type="text/javascript">
        // Wait until network is initialized
        setTimeout(() => {
            if (typeof network === 'undefined' || typeof nodes === 'undefined') return;

            // Store the original node styles
            const originalNodes = JSON.parse(JSON.stringify(nodes.get()));

            // Function to reset all node borders
            function resetNodeBorders() {
                const updated = nodes.get().map(n => ({ id: n.id, borderWidth: 1, color: { border: n.color.border || 'black', background: n.color.background || n.color } }));
                nodes.update(updated);
            }

            // On node click
            network.on("click", function (params) {
                resetNodeBorders();
                if (params.nodes.length > 0) {
                    const clickedId = params.nodes[0];
                    const clickedNode = nodes.get(clickedId);
                    if (!clickedNode || !clickedNode.label) return;

                    // Find nodes with same label
                    const sameLabelNodes = nodes.get().filter(n => n.label === clickedNode.label);

                    // Highlight them
                    sameLabelNodes.forEach(n => {
                        nodes.update({
                            id: n.id,
                            borderWidth: 5,
                            color: { border: 'black', background: n.color.background || n.color }
                        });
                    });
                }
            });
        }, 500);
        </script>
        """
    html_content = html_content.replace("</body>", highlight_js + "\n</body>")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

def generate_color_map(m):
    """Generate m distinct colors using a colormap."""
    colors = cm.rainbow(np.linspace(0, 1, m))  # Get m colors from the rainbow colormap
    color_map = {i + 1: "#{:02x}{:02x}{:02x}".format(
        int(colors[i][0] * 255),
        int(colors[i][1] * 255),
        int(colors[i][2] * 255)
    ) for i in range(m)}
    return color_map


def display_graph(graph, result, obj_func):

    color_map_edges = generate_color_map(len(result))
    for i, vehicle in enumerate(result):
        vehicle.index = i
    color_map_nodes = {1: '#763752', 2: '#99ced6', 3: '#9596c1'}

    coloring_nodes = {}
    for node in graph.nodes():
        coloring_nodes[node.index] = color_map_nodes.get(node.type)

    edge_coloring = {}
    for vehicle in result:
        color = color_map_edges.get(vehicle.index + 1)
        path = vehicle.path
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge_coloring[(u.index, v.index)] = color

    display_colored_graph(graph, coloring_nodes, edge_coloring, color_map_nodes, color_map_edges, obj_func)