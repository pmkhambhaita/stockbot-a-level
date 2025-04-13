import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]

class PathFinder:
    def __init__(self, grid):
        self.grid = grid
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        logger.info(f"PathFinder initialized with grid size {grid.rows}x{grid.cols}")

    def bfs(self, start, end):
        logger.info(f"Starting BFS search from {start} to {end}")
        if not (0 <= start[0] < self.grid.rows and 0 <= start[1] < self.grid.cols):
            logger.error(f"Start position {start} is out of bounds")
            return None
        if not (0 <= end[0] < self.grid.rows and 0 <= end[1] < self.grid.cols):
            logger.error(f"End position {end} is out of bounds")
            return None

        queue = [[start]]
        visited = set()
        
        while queue:
            path = queue.pop(0)
            x, y = path[-1]

            if (x, y) == end:
                logger.info(f"Path found with length {len(path)}")
                return path

            if (x, y) not in visited:
                visited.add((x, y))
                for dx, dy in self.directions:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid.rows and 0 <= ny < self.grid.cols:
                        if (nx, ny) not in visited:
                            new_path = list(path) + [(nx, ny)]
                            queue.append(new_path)

        logger.warning(f"No path found between {start} and {end}")
        return None

    def find_path_through_points(self, start, points, end):
        logger.info(f"Finding path through {len(points)} intermediate points")
        if not points:
            logger.warning("No intermediate points provided")
            return self.bfs(start, end)

        full_path = []
        current_start = start

        for i, point in enumerate(points, 1):
            logger.debug(f"Finding path segment {i} to point {point}")
            path_segment = self.bfs(current_start, point)
            if path_segment:
                full_path.extend(path_segment[:-1])
                current_start = point
            else:
                logger.error(f"Failed to find path segment to point {point}")
                return None

        final_segment = self.bfs(current_start, end)
        if final_segment:
            full_path.extend(final_segment)
            logger.info(f"Complete path found with length {len(full_path)}")
            return full_path
        else:
            logger.error(f"Failed to find final path segment to end point {end}")
            return None

class PathVisualiser:
    def __init__(self, grid):
        self.grid = grid
        logger.info(f"PathVisualiser initialized with grid size {grid.rows}x{grid.cols}")

    def visualise_path(self, path, start, end, points=[]):
        if not path:
            logger.error("Cannot visualize: path is empty or None")
            return

        logger.info("Starting path visualization")
        try:
            visual_grid = [['[ ]' for _ in range(self.grid.cols)] for _ in range(self.grid.rows)]

            for (x, y) in path:
                visual_grid[x][y] = '[=]'

            sx, sy = start
            ex, ey = end
            visual_grid[sx][sy] = '[*]'
            visual_grid[ex][ey] = '[*]'
            
            for x, y in points:
                if 0 <= x < self.grid.rows and 0 <= y < self.grid.cols:
                    visual_grid[x][y] = '[*]'
                else:
                    logger.warning(f"Point ({x}, {y}) is out of bounds and will be skipped")

            for row in visual_grid:
                print(' '.join(row))
            
            logger.info("Path visualization completed")
        except Exception as e:
            logger.error(f"Error during visualization: {str(e)}")

# Update the example usage with error handling
try:
    rows, cols = 10, 10
    grid = Grid(rows, cols)
    path_finder = PathFinder(grid)
    path_visualiser = PathVisualiser(grid)

    start_node = (0, 0)
    end_node = (rows - 1, cols - 1)
    intermediate_points = [(2, 2), (5, 5), (7, 7)]

    logger.info("Starting pathfinding process")
    path_in = path_finder.find_path_through_points(start_node, intermediate_points, end_node)
    
    if path_in:
        path_visualiser.visualise_path(path_in, start_node, end_node, intermediate_points)
    else:
        logger.error("Failed to find a valid path through all points")
except Exception as e:
    logger.error(f"An unexpected error occurred: {str(e)}")