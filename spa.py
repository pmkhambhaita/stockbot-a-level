# Import logging module for tracking programme execution
import logging
import random  # For genetic algorithm
import math    # For distance calculations

# Configure logging settings for output formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up logging to write to both file and terminal
file_handler = logging.FileHandler('stockbot_log.txt')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Grid class represents the warehouse structure
class Grid:
    def __init__(self, rows_grid, cols_grid):
        # Store grid dimensions
        self.rows = rows_grid
        self.cols = cols_grid
        # Initialise empty grid with specified dimensions
        self.grid = [[0 for _ in range(cols_grid)] for _ in range(rows_grid)]

# PathFinder class implements the pathfinding algorithm
class PathFinder:
    def __init__(self, grid_in=None):
        # Store reference to the grid
        self.grid = grid_in
        # Define possible movement directions (up, down, left, right)
        self.directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if grid_in:
            logger.info(f"PathFinder initialised with grid size {grid_in.rows}x{grid_in.cols}")

    def bfs(self, start, end):
        # Implements Breadth-First Search algorithm to find shortest path
        logger.info(f"Starting BFS search from {start} to {end}")
        # Validate start and end positions are within grid boundaries
        if not (0 <= start[0] < self.grid.rows and 0 <= start[1] < self.grid.cols):
            logger.error(f"Start position {start} is out of bounds")
            return None
        if not (0 <= end[0] < self.grid.rows and 0 <= end[1] < self.grid.cols):
            logger.error(f"End position {end} is out of bounds")
            return None

        # Initialise queue with starting point and visited set
        queue = [[start]]
        visited = set()
        
        # Continue searching while there are paths to explore
        while queue:
            path = queue.pop(0)  # Get the next path to explore
            x, y = path[-1]      # Get the last point in the path

            # Check if we've reached the destination
            if (x, y) == end:
                logger.info(f"Path found with length {len(path) - 1}")
                return path

            # Explore unvisited neighbours
            if (x, y) not in visited:
                visited.add((x, y))
                for dx, dy in self.directions:
                    nx, ny = x + dx, y + dy  # Calculate neighbour coordinates
                    # Check if neighbour is within bounds
                    if 0 <= nx < self.grid.rows and 0 <= ny < self.grid.cols:
                        if (nx, ny) not in visited:
                            new_path = list(path) + [(nx, ny)]
                            queue.append(new_path)

        logger.warning(f"No path found between {start} and {end}")
        return None

    def find_path_through_points(self, start, points, end, optimize_order=False):
        """
        Finds a path that visits all intermediate points
        
        Parameters:
        - start: Starting position
        - points: List of intermediate points to visit
        - end: End position
        - optimize_order: Whether to optimize the order of points using genetic algorithm
        """
        logger.info(f"Finding path through {len(points)} intermediate points")
        
        if not points:
            logger.warning("No intermediate points provided")
            return self.bfs(start, end)
                
        # If optimize_order is True, find the optimal order to visit points
        if optimize_order and len(points) > 1:
            points = self.optimize_point_order(start, points, end)
            logger.info(f"Optimized point order: {points}")

        # Initialise path construction
        full_path = []
        current_start = start

        # Find path segments between consecutive points
        for i, point in enumerate(points, 1):
            logger.debug(f"Finding path segment {i} to point {point}")
            path_segment = self.bfs(current_start, point)
            if path_segment:
                full_path.extend(path_segment[:-1])
                current_start = point
            else:
                logger.error(f"Failed to find path segment to point {point}")
                return None

        # Find final path segment to end point
        final_segment = self.bfs(current_start, end)
        if final_segment:
            full_path.extend(final_segment)
            logger.info(f"Complete path found with length {len(full_path) - 1}")
            return full_path
        else:
            logger.error(f"Failed to find final path segment to end point {end}")
            return None
            
    def optimize_point_order(self, start, points, end):
        """
        Optimizes the order of points to minimize total path length
        using a genetic algorithm approach
        """
        logger.info("Optimizing point order using genetic algorithm")
        
        # If only one point, no optimization needed
        if len(points) <= 1:
            return points
            
        # Create initial population (different permutations of points)
        population_size = min(100, math.factorial(len(points)))
        population = []
        
        # Add the original order
        population.append(list(points))
        
        # Add random permutations
        while len(population) < population_size:
            perm = list(points)
            random.shuffle(perm)
            if perm not in population:
                population.append(perm)
                
        # Number of generations
        generations = 20
        
        # For each generation
        for gen in range(generations):
            # Calculate fitness for each permutation
            fitness_scores = []
            
            for perm in population:
                # Calculate total path length
                total_length = 0
                
                # Start to first point
                if self.grid.rows <= 10 and self.grid.cols <= 10:
                    # For small grids, we can use exact path length
                    path = self.bfs(start, perm[0])
                    if path:
                        total_length += len(path) - 1
                    else:
                        total_length += 999  # Large penalty for impossible paths
                else:
                    # For larger grids, use Manhattan distance as an approximation
                    total_length += abs(start[0] - perm[0][0]) + abs(start[1] - perm[0][1])
                
                # Between points
                for i in range(len(perm) - 1):
                    if self.grid.rows <= 10 and self.grid.cols <= 10:
                        path = self.bfs(perm[i], perm[i+1])
                        if path:
                            total_length += len(path) - 1
                        else:
                            total_length += 999
                    else:
                        total_length += abs(perm[i][0] - perm[i+1][0]) + abs(perm[i][1] - perm[i+1][1])
                
                # Last point to end
                if self.grid.rows <= 10 and self.grid.cols <= 10:
                    path = self.bfs(perm[-1], end)
                    if path:
                        total_length += len(path) - 1
                    else:
                        total_length += 999
                else:
                    total_length += abs(perm[-1][0] - end[0]) + abs(perm[-1][1] - end[1])
                
                # Fitness is inverse of length (shorter is better)
                fitness = 1000.0 / (total_length + 1)
                fitness_scores.append((fitness, perm))
            
            # Sort by fitness (descending)
            fitness_scores.sort(reverse=True)
            
            # Select top performers
            top_performers = [perm for _, perm in fitness_scores[:population_size//2]]
            
            # Create new population
            new_population = list(top_performers)
            
            # Add crossover children
            while len(new_population) < population_size:
                # Select two parents
                parent1 = random.choice(top_performers)
                parent2 = random.choice(top_performers)
                
                # Create child using ordered crossover
                child = self._ordered_crossover(parent1, parent2)
                
                # Add to new population
                if child not in new_population:
                    new_population.append(child)
            
            # Apply mutation
            for i in range(1, len(new_population)):
                if random.random() < 0.1:  # 10% mutation rate
                    self._mutate(new_population[i])
            
            # Update population
            population = new_population
            
            logger.debug(f"Generation {gen+1}: Best fitness = {fitness_scores[0][0]}")
        
        # Return the best permutation
        return fitness_scores[0][1]
    
    def _ordered_crossover(self, parent1, parent2):
        """Helper method for genetic algorithm crossover"""
        size = len(parent1)
        
        # Select a random subset of parent1
        start, end = sorted(random.sample(range(size), 2))
        
        # Create child with subset from parent1
        child = [None] * size
        for i in range(start, end + 1):
            child[i] = parent1[i]
        
        # Fill remaining positions with values from parent2 in order
        parent2_idx = 0
        for i in range(size):
            if child[i] is None:
                while parent2[parent2_idx] in child:
                    parent2_idx += 1
                child[i] = parent2[parent2_idx]
                parent2_idx += 1
        
        return child
    
    def _mutate(self, permutation):
        """Helper method for genetic algorithm mutation"""
        # Swap two random positions
        idx1, idx2 = random.sample(range(len(permutation)), 2)
        permutation[idx1], permutation[idx2] = permutation[idx2], permutation[idx1]

# PathVisualiser class handles the visual representation of the path
class PathVisualiser:
    def __init__(self, grid_in):
        # Store reference to the grid
        self.grid = grid_in
        logger.info(f"PathVisualiser initialised with grid size {grid_in.rows}x{grid_in.cols}")

    def visualise_path(self, path, start, end, points=None):
        # Creates a visual representation of the path using ASCII characters
        # [ ] represents empty cells
        # [=] represents path segments
        # [*] represents start, end, and intermediate points
        if points is None:
            points = []
        if not path:
            logger.error("Cannot visualise: path is empty or None")
            return

        logger.info("Starting path visualisation")
        try:
            # Create empty visual grid
            visual_grid = [['[ ]' for _ in range(self.grid.cols)] for _ in range(self.grid.rows)]

            # Mark path segments
            for (x, y) in path:
                visual_grid[x][y] = '[=]'

            # Mark start and end points
            sx, sy = start
            ex, ey = end
            visual_grid[sx][sy] = '[*]'
            visual_grid[ex][ey] = '[*]'
            
            # Mark intermediate points
            for x, y in points:
                valid, _ = validate_point(x, y, self.grid.rows, self.grid.cols, True)
                if valid:
                    visual_grid[x][y] = '[*]'
                else:
                    logger.warning(f"Point ({x}, {y}) is out of bounds and will be skipped")

            # Display the grid
            for row in visual_grid:
                print(' '.join(row))
            
            logger.info("Path visualisation completed")
        except Exception as _e_:
            logger.error(f"Error during visualisation: {str(_e_)}")

def validate_point(x, y, rows, cols, allow_start_end=False):
    """Validates if a point is within bounds and optionally checks for start/end points"""
    # Check if point is start/end when not allowed
    if not allow_start_end and ((x, y) == (0, 0) or (x, y) == (rows - 1, cols - 1)):
        return False, f"Cannot use start point (index 1) or end point (index {rows * cols})"
    
    # Check if point is within grid boundaries
    if not (0 <= x < rows and 0 <= y < cols):
        return False, f"Position out of bounds"
    
    return True, ""

# Add after the existing imports
def index_to_coordinates(index, cols):
    """Convert 1-based index to 0-based coordinates"""
    index -= 1  # Convert to 0-based
    row = index // cols
    col = index % cols
    return row, col

def coordinates_to_index(row, col, cols):
    """Convert 0-based coordinates to 1-based index"""
    return (row * cols) + col + 1