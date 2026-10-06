try:
    import pandas as pd  # type: ignore
except ModuleNotFoundError:
    pd = None  # type: ignore[assignment]

import heapq


def load_graph_from_excel(filename):
    """
    Reads the Excel file and builds an adjacency list graph 
    from the city distance matrix.
    """
    if pd is None:
        raise ModuleNotFoundError("pandas is required to read the Excel file.")

    df = pd.read_excel(filename, sheet_name='Sheet1')
    cities_df = df.iloc[:17].copy()  # First 17 rows are the cities
    cities = cities_df['City'].tolist()
    
    graph = {}
    for _, row in cities_df.iterrows():
        city = row['City']
        graph[city] = []
        for target_city in cities:
            if city == target_city:
                continue
            distance = row[target_city]
            # Add valid numerical distances as graph edges
            if pd.notna(distance) and distance != '':
                graph[city].append((target_city, float(distance)))
                
    return graph, cities_df.set_index('City')

def run_a_star(filename, start_city, target_city):
    """
    Main function called by your main.py file. 
    Accepts the Excel filename parameter and executes A* search.
    """
    graph, cities_df = load_graph_from_excel(filename)
    
    # Heuristic h(n): distance from current node to target city using the matrix
    def get_heuristic(node):
        if node == target_city:
            return 0.0
        try:
            val = cities_df.loc[node, target_city]
            if pd.notna(val):
                return float(val)
        except KeyError:
            pass
        return 0.0

    if start_city == target_city:
        return [start_city], 0
        
    pq = [(get_heuristic(start_city), 0, start_city, [start_city])]
    g_scores = {start_city: 0}
    closed_set = set()

    while pq:
        f, g, current, path = heapq.heappop(pq)

        if current == target_city:
            return path, g

        if current in closed_set:
            continue
        closed_set.add(current)

        for neighbor, weight in graph.get(current, []):
            if neighbor in closed_set:
                continue
            
            tentative_g = g + weight

            if tentative_g < g_scores.get(neighbor, float('inf')):
                g_scores[neighbor] = tentative_g
                h = get_heuristic(neighbor)
                f = tentative_g + h
                heapq.heappush(pq, (f, tentative_g, neighbor, path + [neighbor]))

    return None, float('inf')