import pandas as pd

def read_csv_file(file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)   
    return df


