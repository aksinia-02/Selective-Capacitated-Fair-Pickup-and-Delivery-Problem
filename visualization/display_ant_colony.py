import pygame
import sys
import networkx as nx
import random


class LiveGraph:
    def __init__(
        self, graph: nx.Graph,
        width=900, height=600, title="SCF-PDP – Pheromone Graph",
        bg_color=(220, 220, 220), 
        node_color_pickup=(153,206,214),
        node_color_dropoff=(149,150,193),
        node_color_depot=(118,55,82),
        pheromone_color=(0, 220, 255),
        node_radius=7, pheromone_threshold=1e-6
    ):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()

        self.graph = graph
        self.width = width
        self.height = height

        self.bg_color = bg_color
        self.node_color_pickup = node_color_pickup
        self.node_color_dropoff = node_color_dropoff
        self.node_color_depot = node_color_depot
        self.pheromone_color = pheromone_color
        self.node_radius = node_radius
        self.pheromone_threshold = pheromone_threshold

        self.dragging_node = None

        self.font = pygame.font.SysFont("consolas", 14)

        self.pos = {}
        self._compute_positions_from_coordinates()

    def _compute_positions_from_coordinates(self):
        xs = [n.x for n in self.graph.nodes]
        ys = [n.y for n in self.graph.nodes]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        margin = 100

        for n in self.graph.nodes:
            x = n.x
            y = n.y

            sx = margin + (x - min_x) / (max_x - min_x) * (self.width - 2 * margin)
            sy = margin + (y - min_y) / (max_y - min_y) * (self.height - 2 * margin)

            self.pos[n] = (int(sx), int(sy))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for node, (x, y) in self.pos.items():
                    if (mx - x) ** 2 + (my - y) ** 2 <= self.node_radius ** 2:
                        self.dragging_node = node
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging_node = None

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_node is not None:
                    self.pos[self.dragging_node] = pygame.mouse.get_pos()

    # Rendering
    def draw_pheromone_edges(self):
        for u, v, data in self.graph.edges(data=True):
            pheromone = data.get("pheromone", 0.0)

            if pheromone <= self.pheromone_threshold:
                continue

            x1, y1 = self.pos[u]
            x2, y2 = self.pos[v]

            width = max(1, int(2 + 6 * pheromone))

            pygame.draw.line(
                self.screen,
                self.pheromone_color,
                (x1, y1),
                (x2, y2),
                width
            )

    def draw_nodes(self):
        for node, (x, y) in self.pos.items():
            if node.type == 1:
                pygame.draw.circle(self.screen, self.node_color_depot, (x, y), self.node_radius)
            elif node.type == 2:
                pygame.draw.circle(self.screen, self.node_color_pickup, (x, y), self.node_radius)
            else:
                pygame.draw.circle(self.screen, self.node_color_dropoff, (x, y), self.node_radius)

            label = self.font.render(f"{node.index}", True, (51, 0, 25))
            self.screen.blit(label, (x + 8, y - 8))

    def render(self):
        self.screen.fill(self.bg_color)
        self.draw_pheromone_edges()
        self.draw_nodes()
        pygame.display.flip()
        self.clock.tick(60)
