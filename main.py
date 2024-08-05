import os
import hashlib
import datetime
import numpy as np
import pandas as pd
from util import read_csv_file
from dataengineering import read_dataset, sample_dataframe, generate_fight
import random
import ipywidgets as widgets
from IPython.display import display
import PySimpleGUI as sg
import seaborn as sns
import matplotlib.pyplot as plt

# Function to prepare the hero list from the dataframe
def extract_unique_heroes(df):
    heroes = set(df['Sup_1_Character']).union(set(df['Sup_2_Character']))
    return list(heroes)


# Function to randomly swap values
def randomly_swap(row):
    if np.random.rand() > 0.5:  # 50% chance to swap
        row['Sup_1_Character'], row['Sup_2_Character'] = row['Sup_2_Character'], row['Sup_1_Character']
    return row


def handle_result(result, hero_left, hero_right, result_df, total_questions_asked):
    
    result_df.loc[len(result_df)] = [hero_left, hero_right, result]
    print(len(result_df))
    print('')
    
    total_questions_asked -= 1
    if total_questions_asked > 0:
        ask_question(result_df, total_questions_asked)
        print(f'Remaining questions to ask: {total_questions_asked}')
    else:
        print("All questions asked. Here are the results:")
        print(result_df)
    return result_df


# Function to ask a question in the console
def ask_question(results_df, total_questions_asked):
    hero_left = random.choice(unique_heroes)
    hero_right = random.choice(new_heroes)
    
    print(f"Who wins? {hero_left} (left) or {hero_right} (right)?")
    print("L: Left Wins")
    print("R: Right Wins")
    print("D: Draw")

    valid_input = False
    while not valid_input:
        choice = input("Enter your choice (L/R/D): ")
        if choice == "L":
            results_df = handle_result(hero_left, hero_left, hero_right, results_df, total_questions_asked)
            valid_input = True
        elif choice == "R":
            results_df = handle_result(hero_right, hero_left, hero_right, results_df, total_questions_asked)
            valid_input = True
        elif choice == "D":
            results_df = handle_result("Draw", hero_left, hero_right, results_df, total_questions_asked)
            valid_input = True
        else:
            print("Invalid choice. Please enter L, R, or D.")
    return results_df


if __name__ == "__main__":
    dataset_percentage_used = 100 
    main_dir = os.path.dirname(os.path.abspath(__file__))
    
    print('---------------------\n-- READING DATASET --\n---------------------')
    # dataset_name: dataset_01 / dataset_02
    df = read_dataset('dataset_01', main_dir)

    # Sample the dataframe based on the specified percentage
    df_sampled = sample_dataframe(df, dataset_percentage_used)
    
    print(f'This is the length of the fight-dataset sampled: {len(df_sampled)}' )
    
    # Initialize an empty list to collect all simulated fights
    all_simulated_fights = []

    # Iterate over each row in the dataframe
    for index, row in df_sampled.iterrows():
        #print(f'Current fight: {index}')
        simulated_fights_df = generate_fight(row)
        all_simulated_fights.append(simulated_fights_df)

    # Concatenate all simulated fights into a single dataframe
    all_simulated_fights_df = pd.concat(all_simulated_fights, ignore_index=True)
    print(f'This is the length of the simulated fight-dataset created: {len(all_simulated_fights_df)}')

    # Display the first few rows of the simulated fights
    print('\nTHESE ARE THE SIMULATED FIGHTS')
    print(simulated_fights_df.head())

    # Extract unique heroes
    unique_heroes = extract_unique_heroes(df)

    # Display the list of unique heroes
    print("List of unique heroes:")
    for hero in unique_heroes[0:10]:
        print(hero)


    # Define the new heroes list
    new_heroes = ["Velociraptor", "10 x Velociraptor", "100 x Velociraptors", "1000 x Velociraptors"]

    # Ask for the number of questions
    total_questions_asked = int(input("Enter the number of questions to be asked: "))

    # Dataframe to store results
    results_df = pd.DataFrame(columns=['Sup_1_Character', 'Sup_2_Character', 'Result_fight'])

    # Start asking questions
    #survey_df = ask_question()
   
    survey_df = ask_question(results_df, total_questions_asked)

    # Combine the dataframes
    survey_df.columns = survey_df.columns.str.strip()
    all_simulated_fights_df.columns = all_simulated_fights_df.columns.str.strip()
    combined_df = pd.concat([all_simulated_fights_df, survey_df], ignore_index=True)
    print(survey_df)


    # Apply the function to each row
    survey_df = survey_df.apply(randomly_swap, axis=1)

    # AMPLIFY YOUR VOTES Duplicate the dataframe 7 times
    amplified_survey_df = pd.concat([survey_df] * 10000, ignore_index=True)
    print(amplified_survey_df)

    combination_df = pd.concat([all_simulated_fights_df, amplified_survey_df], ignore_index=True)

    # Get all unique elements of the 'Sup_1_Character' column
    unique_sup_2_characters = combination_df['Sup_2_Character'].unique()

    ################
    #
    #      ELO
    #
    ################


    # Initialize ELO ratings
    elo_ratings = {}

    def get_elo(character):
        if character not in elo_ratings:
            elo_ratings[character] = 1000  # Default starting ELO
        return elo_ratings[character]

    def update_elo(winner, loser):
        k = 32  # K-factor for ELO rating adjustment
        winner_rating = get_elo(winner)
        loser_rating = get_elo(loser)
    
        expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
        expected_loser = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))
    
        new_winner_rating = winner_rating + k * (1 - expected_winner)
        new_loser_rating = loser_rating + k * (0 - expected_loser)
    
        elo_ratings[winner] = new_winner_rating
        elo_ratings[loser] = new_loser_rating

    # Process each fight in the dataframe
    for index, row in combination_df.iterrows():
        winner = row['Result_fight']
        loser = row['Sup_1_Character'] if row['Result_fight'] == row['Sup_2_Character'] else row['Sup_2_Character']
        update_elo(winner, loser)

    # Convert the ELO ratings to a dataframe and sort by rating
    elo_df = pd.DataFrame(list(elo_ratings.items()), columns=['Character', 'ELO'])
    elo_df = elo_df.sort_values(by='ELO', ascending=False).reset_index(drop=True)

    print(elo_df)


    ########################
    #
    #      SAVE TO FILE
    #
    ########################

    # Generate current date string
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Generate a unique hash
    unique_hash = hashlib.md5(os.urandom(32)).hexdigest()[:8]

    # Create the filename prefix
    filename_prefix = f"{current_date}_{unique_hash}_elo_ranking"

    # Save the dataframe to a CSV file
    csv_filename = f"{filename_prefix}.csv"
    elo_df.to_csv(csv_filename, index=False)
    print(f"DataFrame saved to CSV file: {csv_filename}")

    # Save the dataframe to an Excel file
    excel_filename = f"{filename_prefix}.xlsx"
    elo_df.to_excel(excel_filename, index=False)
    print(f"DataFrame saved to Excel file: {excel_filename}")

    ###################################
    #
    #      READ OBJECTIVE MEASURES
    #
    ###################################

    df = pd.read_excel(main_dir+'/data/superherodb-com.xlsx') 
    # Remove rows where "Strength", "Speed", and "Durability" are missing
    df_cleaned = df.dropna(subset=["Strength", "Speed", "Durability"], how='all')

    # Display the cleaned dataframe
    print("\nCleaned DataFrame:")
    print(df_cleaned)
    
    # Merge the dataframes on the "Character" column
    combined_df = pd.merge(elo_df, df_cleaned, on='Character', how='inner')

    # Display the combined dataframe
    print("\nCombined DataFrame:")
    print(combined_df)

    # Create a pairplot using seaborn
    sns.pairplot(combined_df[['ELO', 'Strength', 'Speed', 'Durability']])
    plt.suptitle('Pairplot of ELO, Strength, Speed, and Durability', y=1.02)
    plt.show()

  