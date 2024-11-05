import pandas as pd
import numpy as np
from pandastable import Table
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.filedialog import asksaveasfilename

searchList = ["SPLASHES", "GRAZES", "attacks", "CRITICALS", 'DRAINS', 'RAMS', "GRAPPLES", "HACKS", "TAUNTS", "DEFLECTS"]
attack_types = ['GRAZES', 'attacks', 'CRITICALS', 'SPLASHES']
ShipNames = ['Emp-1','Emp-2','Emp-3', 'Emp-4', 'Emp-5', 'Emp-6', 'Emp-7', "Boondog's Het Stinger-I", "Boondog's Striker Gunboat-IV-ULT"]

def open_txt():
    global df
    filetypes = (('Text files', '*.txt'), ('All files', '*.*'))
    filename = fd.askopenfilename(title='Open a file', initialdir='/', filetypes=filetypes)

    if filename:
        with open(filename, 'r') as file:
            lines = [value for i, value in enumerate(file) if i % 2 != 0]
            df = pd.DataFrame(lines, columns=['Heading1'])
            clean_data(df)
            df = calc_stats(df)
            display_stats(df)

def close_window():
    root.destroy()

def save_to_csv():
    global df
    file_path = asksaveasfilename(defaultextension=".csv",
    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
    initialdir="C:/Users/YourUsername/Downloads")
    if file_path:
        df.to_csv(file_path, index=False)

def clean_data(df):
    for col in df.columns:
        df[col] = df[col].str.replace('[', '')
        df[col] = df[col].str.replace(']', '')
        df[col] = df[col].str.replace('(', '')
        df[col] = df[col].str.replace(')', '')
        df[col] = df[col].str.replace(r'<.*?>', '', regex=True)

    pattern = '|'.join(searchList)
    df['Ship'] = df['Heading1'].str.split(f'({pattern})').str[0]
    df["Att_Type"] = df['Heading1'].str.extract(f'({pattern})', expand=False)
    df["Att_Type"] = df["Att_Type"].fillna('')

    # List of word pairs to search for
    word_pairs = [
        ('HACKS', 'for'),
        ('TAUNTS', 'for'),
        ('GRAPPLES', 'for'),
        ('DRAINS', 'of'),
        ('RAMS', 'for')
    ]

    # Initialize the 'OtherAtt' column
    df['OtherAtt'] = np.nan
    # Create a regular expression pattern to extract text between the two words
    for word1, word2 in word_pairs:
        pattern = fr'{word1}\s*(.*?)\s*{word2}'
        df['OtherAtt'] = df['OtherAtt'].combine_first(df['Heading1'].str.extract(pattern, expand=False))
        df['OtherAtt'] = df['OtherAtt'].fillna('')

    # Create a regular expression pattern to find numeric values after the specific word
    specific_word = 'for'
    pattern = fr'{specific_word}\s+(\d+)'

    # Extract numeric value directly after the specific word
    df['HullDmg'] = df['Heading1'].str.extract(pattern, expand=False)
    df['HullDmg'] = df['HullDmg'].fillna('0')

    # Create a regular expression pattern to find numeric values after the specific word
    specific_word = 'and'
    pattern = fr'{specific_word}\s+(\d+)'

    # Extract numeric value directly after the specific word
    df['ShieldDmg'] = df['Heading1'].str.extract(pattern, expand=False)
    df['ShieldDmg'] = df['ShieldDmg'].fillna('0')

    df['TotalDmg'] = pd.to_numeric(df['HullDmg']) + pd.to_numeric(df['ShieldDmg'])
    df['TotalDmg'] = df['TotalDmg'].fillna('')

    # Define the two words to search between
    word1 = 'with'
    word2 = 'for'
    # Create a regular expression pattern to extract text between the two words
    pattern = fr'{word1}\s*(.*?)\s*{word2}'
    df['Weapon'] = df['Heading1'].str.extract(pattern, expand=False)
    df['Weapon'] = df['Weapon'].fillna('')

    df['ID'] = range(len(df))

def calc_stats(df):
    df.drop(columns=df.columns[0], axis=1, errors='ignore', inplace=True)
    headers = ['Ship', "Att_Type", 'OtherAtt', 'HullDmg', 'ShieldDmg', 'TotalDmg', 'Weapon', 'ID']
    df = pd.DataFrame(df, columns=headers)
    df = df.drop(columns=['HullDmg', 'ShieldDmg', 'OtherAtt'])

    # Iterate through the DataFrame rows
    #df['splash_check'] = ''
    #df['splash_check2'] = ''
    for i in range(len(df)):
        #print(df["Att_Type"].iloc[i])
        #print(df.at[i, "Att_Type"])
        if df["Att_Type"].iloc[i] == 'SPLASHES':
            #df.at[i, 'splash_check'] = 'Yes'
            if df.iloc[i]['Ship'] == df.iloc[i - 1]['Ship']:
                #df.at[i, 'splash_check2'] = 'Yes'
                df.at[i, 'Weapon'] = df.iloc[i - 1]['Weapon']

    df = df[~df["Ship"].str.contains("DESTROYED")]
    df = df[~df["Ship"].str.contains("wormhole")]
    df = df[~df["Ship"].str.contains("XP")]
    df = df[~df["Ship"].str.contains("RAMMED")]
    df = df[~df["Ship"].str.contains("DRAGGED")]
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    df=df[df['Weapon'].str.len() > 0]

    #=================================================
    # Convert DataFrame to List of Lists
    list_of_lists = df.values.tolist()

    # Write the List of Lists to a .py File
    with open('ListofLists.py', 'w') as file:
        file.write('list_of_lists = ' + str(list_of_lists))

    #print(list_of_lists)
    #================================================
    #================================================
    # Copy DataFrame
    df_copy = df.copy()

    # Write the copied DataFrame to a .py file
    with open('CopiedDataFrame.py', 'w') as file:
        file.write("import pandas as pd\n\n")
        file.write("data = [\n")
        for row in df_copy.values.tolist():
            file.write(f"    {row},\n")
        file.write("]\n\n")
        file.write("headers = ['Ship', 'Att_Type', 'TotalDmg', 'Weapon']\n\n")
        file.write("df_copy = pd.DataFrame(data, columns=headers)\n")

    #print("DataFrame has been copied to 'CopiedDataFrame.py'")

    #================================================
    # Initialize a list to store results for all ships
    all_ships_results = []

    for Ship1 in ShipNames:
        # Filter the DataFrame for the current ship and remove rows with blank 'Weapon' values
        filtered_df = df[(df['Ship'] == Ship1) & df['Weapon'].notna()]
        if filtered_df.empty:
            continue  # Skip the ship if there are no records

        # Get unique weapon values, excluding blanks
        unique_values = filtered_df['Weapon'].unique().tolist()
        remove_blanks = [item for item in unique_values if item]

        # Initialize a dictionary to store results for each weapon
        weapon_stats = {}

        # Calculate sum and count for each weapon, separated by attack type
        for weapon in filtered_df['Weapon'].unique():
            stats = {
                'total_dmg': int(filtered_df[filtered_df['Weapon'] == weapon]['TotalDmg'].sum()),
                'count': int(
                    filtered_df[(filtered_df['Weapon'] == weapon) & (filtered_df["Att_Type"] != 'SPLASHES')].shape[0])
            }
            for attack in attack_types:
                filtered_attack_df = filtered_df[
                    (filtered_df['Weapon'] == weapon) & (filtered_df["Att_Type"].str.upper() == attack.upper())]
                total_dmg = int(filtered_attack_df['TotalDmg'].sum())
                count = int(filtered_attack_df.shape[0])
                stats[f'{attack.lower()}_dmg'] = total_dmg
                stats[f'{attack.lower()}_count'] = count
            stats['avg_dmg'] = stats['total_dmg'] // stats['count'] if stats['count'] > 0 else 0
            weapon_stats[weapon] = stats

        # Create a list of results for the current ship
        results_list = [
            [
                Ship1,
                weapon,
                stats['total_dmg'],
                stats['avg_dmg'],
                stats['count'],
                stats.get('grazes_dmg', 0), stats.get('grazes_count', 0),
                stats.get('attacks_dmg', 0), stats.get('attacks_count', 0),
                stats.get('criticals_dmg', 0), stats.get('criticals_count', 0),
                stats.get('splashes_dmg', 0), stats.get('splashes_count', 0)
            ]
            for weapon, stats in weapon_stats.items()
        ]

        all_ships_results.extend(results_list)

    # Create a new DataFrame from the combined results
    columns = ['Ship', 'Weapon', 'TotalDmg', 'AvgDmg', 'Count',
               'GrazesDmg', 'GrazesCount', 'AttacksDmg', 'AttacksCount',
               'CriticalsDmg', 'CriticalsCount', 'SplashesDmg', 'SplashesCount']
    df = pd.DataFrame(all_ships_results, columns=columns)
    print(df)
    return df

def display_stats(df):
    print(df)
    # Ensure the frame is defined
    frame = ttk.Frame(root, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)

    # Create vertical scrollbar
    v_scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create horizontal scrollbar
    h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    # Display the results DataFrame
    tree = ttk.Treeview(frame, columns=list(df.columns), show='headings', yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    # Insert DataFrame rows into the table
    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Configure the scrollbars to work with the treeview
    v_scrollbar.config(command=tree.yview)
    h_scrollbar.config(command=tree.xview)

    # Changes pandas display settings
    pd.options.display.width = None
    pd.options.display.max_columns = None
    pd.set_option('display.max_rows', 3000)
    pd.set_option('display.max_columns', 3000)

    print(df)

    with open('CleanedData.py', 'w') as CleanedData:
        CleanedData.write(df.to_string(index=False))

root = tk.Tk()
root.title("DataFrame in Tkinter")

# Create a frame for the button
frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)# Create a frame for the button

open_button = ttk.Button(frame, text="Open Txt File", command=open_txt)
open_button.pack(pady=10)

button1 = tk.Button(root, text="Close", command=close_window)
button1.pack()

# Update the button command to pass the DataFrame
save_button = ttk.Button(frame, text="Save to CSV", command=save_to_csv)
save_button.pack(pady=10)

# Create a Text widget to display the file contents
text_widget = tk.Text(frame, wrap='word')
text_widget.pack(fill=tk.BOTH, expand=True)

label = tk.Label(root)
label.pack(padx=10, pady=10)


root.mainloop()
