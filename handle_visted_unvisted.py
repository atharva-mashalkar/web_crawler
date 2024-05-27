import os

# Read visited links from file
def get_links(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return list(line.strip() for line in file)
    return list()



# Save visited links to file
def save_link(link, file_path):
    try:
        with open(file_path, 'a') as file:
            file.write(link + '\n')
    except Exception as e:
        print(f"An error occured: {e}")


# Getting a list of downloaded files
def get_downloaded_links(folder):
    try:
        # Get the list of files in the specified folder
        if not os.path.exists(folder):
            return list()
        
        files = os.listdir(folder)
        
        # Create a list to store the file names
        file_names = list()
        
        for file in files:
            # Add each file name to the set
            if os.path.isfile(os.path.join(folder, file)):
                file_names.append(file)
                
        return file_names
    except Exception as e:
        print(f"An error occurred: {e}")
        return list()
    


