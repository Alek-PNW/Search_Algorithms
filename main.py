import random
import sys
from pathlib import Path

import pandas as pd  # type: ignore[reportMissingModuleSource]

from Loading_Data_from_Excel import run_a_star

def main():
    data_filename = 'CS362_Project1_Data.xlsx'
    
    # Read the city names from the Excel file
    df = pd.read_excel(data_filename, sheet_name='Sheet1')
    all_cities = df.iloc[:17]['City'].tolist()
    
    print("========================================")
    print(" A* Search Algorithm - Excel Data Test")
    print("========================================")
    
    # Test 5 random start and target city pairs as required by your project
    for i in range(1, 6):
        start_city, target_city = random.sample(all_cities, 2)
        
        path, total_distance = run_a_star(data_filename, start_city, target_city)
        
        print(f"\nTest Pair #{i}:")
        print(f"  Start City : {start_city}")
        print(f"  Target City: {target_city}")
        
        if path:
            print(f"  Travel Map : {' -> '.join(path)}")
            print(f"  Total Dist : {total_distance:.2f} miles")
        else:
            print("  No valid path found between these cities.")

if __name__ == "__main__":
    main()