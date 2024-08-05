import os
import numpy as np
import pandas as pd
from util import read_csv_file


def sample_dataframe(df, percentage):
    sample_size = int(len(df) * percentage / 100)
    return df.sample(n=sample_size, random_state=42)


def normalize_probabilities(probabilities, threshold=1e-3):
    # Round probabilities close to 0
    probabilities = [0 if prob < threshold else prob for prob in probabilities]
    
    # Normalize the probabilities to ensure they sum to 1
    total_prob = sum(probabilities)
    if total_prob > 0:
        probabilities = [prob / total_prob for prob in probabilities]
    else:
        # Handle the case where all probabilities are 0 by distributing equally
        probabilities = [1.0 / len(probabilities)] * len(probabilities)
    
    return probabilities


def generate_fight(row):
    sup_1 = row['Sup_1_Character']
    sup_2 = row['Sup_2_Character']
    sup_1_win = row['Superhero_1_win']
    sup_2_win = row['Superhero_2_win']
    draw = row['Draw']
    
    # Create an array of possible outcomes and their probabilities
    outcomes = [sup_1, sup_2, 'Draw']
    probabilities = [sup_1_win / 100, sup_2_win / 100, draw / 100]
    
    # Normalize probabilities
    probabilities = normalize_probabilities(probabilities)
    
    # Generate 100 random outcomes based on the provided probabilities
    results = np.random.choice(outcomes, size=100, p=probabilities)
    
    # Create a dataframe with the results
    data = {
        'Sup_1_Character': [sup_1] * 100,
        'Sup_2_Character': [sup_2] * 100,
        'Result_fight': results
    }
    
    result_df = pd.DataFrame(data)
    
    return result_df


def summarize_fights(df):
    # Create a summary table using the value_counts function
    summary = df['Result_fight'].value_counts().reset_index()
    summary.columns = ['Result_fight', 'Count']

    sup_1_character = df.loc[0, 'Sup_1_Character']
    sup_2_character = df.loc[0, 'Sup_2_Character']
    
    # Convert the summary into a dictionary for easier lookup
    summary_dict = summary.set_index('Result_fight').to_dict()['Count']
    # Extract the counts for each outcome
    sup_1_wins = summary_dict.get(sup_1_character, 0)
    sup_2_wins = summary_dict.get(sup_2_character, 0)
    draws = summary_dict.get('Draw', 0)
    
    # Create a summary dataframe
    summary_df = pd.DataFrame({
        'Result_fight': [sup_1_character, sup_2_character, 'Draw'],
        'Count': [sup_1_wins, sup_2_wins, draws]
    })
    
    return summary_df


def read_dataset(dataset_name, main_directory):
    # Define the mapping of dataset names to file paths
    dataset_mapping = {
        "dataset_01": main_directory+"/data/superhero_battles.csv",
        "dataset_02": main_directory+"/data/superhero_battles_test2_online.csv"
    }

    # Check if the provided dataset name is valid
    if dataset_name not in dataset_mapping:
        raise ValueError("Invalid dataset name provided.")

    # Load the dataset
    file_path = dataset_mapping[dataset_name]
    df = read_csv_file(file_path)

    # Define the list of superheroes to extract if the dataset is dataset_01
    if dataset_name == "dataset_01":
        SUPERHERO_EXTRACTION = ["Superman", "Superman", "Scarlet Witch", 
                                "Lara Croft", "Green Lantern", "Captain Marvel", 
                                "Doctor Strange (Classic)", "Thor", "Robin",
                                "Hulk (Green Scar)", "Batman", "Hulk", 
                                "Aquaman", "Venom", "Ghost Rider", "The Flash", 
                                "Sonic The Hedgehog", "The Rock", "Naruto", 
                                "He-Man", "Wolverine", "Spider-Man", "Bane",
                                "Wonder Woman", "Batgirl", "Krillin", "Yoda", 
                                "Black Panther", "Raiden", "Shao Kahn", "Goku",
                                "Ultron", "Kid Goku",  "Goku (Super Saiyan 3)", 
                                "Superwoman", "King Kong", "Silver Surfer", 
                                "Daredevil", "Iron Man", "Catwoman", 
                                "Supergirl", "Black Adam", "Count Dooku", 
                                "Harry Potter", "Sauron", "Zeus", "Hercules", 
                                "Hancock", "Thanos", "Doctor Doom", "Odin", 
                                "Captain America", "Luke Skywalker", 
                                "Anakin Skywalker", "Brainiac", "Dracula",
                                "Buzz Lightyear", "Homer Simpson", "The Joker", 
                                "Future Trunks (Super Saiyan Rage)", 
                                "Green Power Ranger", "Optimus Prime", 
                                "Mickey Mouse", "Darth Vader", "Peter Pan", 
                                "Muhammad Ali", "Godzilla", "Magneto", 
                                "Goku (Super Saiyan 2)", "Shiva", "Vecna", 
                                "Bob The Builder", "Elsa", "Megatron", 
                                "Qui-Gon Jinn", "Deadpool (Continuity Gem)", 
                                "Mewtwo", "Darth Sidious", "Rocket Raccoon", 
                                "He Who Remains", "Hawkeye", "Deadpool", 
                                "Forrest Gump", "Nick Fury", "Aslan", "Rambo", 
                                "Monkey D. Luffy", "Marvin The Martian", 
                                "Sailor Moon", "Ant-Man", "Super Mario", 
                                "Predator"] 
        
        # Filter the dataframe
        df_filtered = df[(df['Sup_1_Character'].isin(SUPERHERO_EXTRACTION)) &#|
                         (df['Sup_2_Character'].isin(SUPERHERO_EXTRACTION))]
    else:
        df_filtered = df

    return df_filtered
