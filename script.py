import requests
import re
import time
import xml.etree.ElementTree as ET
import random
import os
from dotenv import load_dotenv

load_dotenv()



#this function will get the list of repositories
def repoList(owner):

    url = f"https://api.github.com/users/{owner}/repos"  # f-strings
 
    # Set the headers
    # the headers are used to authenticate the user
    headers = {
        'Authorization': f"token {os.getenv('ACCESS_TOKEN')}",
        'Accept': 'application/vnd.github.v3+json'
    }

    
    repo_list = []

    response = requests.get(url, headers=headers,timeout=5) # Send GET request to the URL
    
    # Check if the request was successful
    if response.status_code == 200:
        print('Success')
        for repo in response.json(): # Loop through the JSON response
            repo_list.append(repo['name']) # Append the name of the repository to the list
        return repo_list # Return the list of repositories
    else:
        print('Error') # Print an error message
        return None
    



#this function will get the files from the repository
def get_path(owner, repository, path=''):
    
    url = f"https://api.github.com/repos/{owner}/{repository}/contents/{path}" # f-strings to insert the owner, repository, and path into the URL

    # Set the headers
    headers = {
        'Authorization': f"token {os.getenv('ACCESS_TOKEN')}",
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(url, headers=headers,timeout=5) # Send GET request to the URL

    if response.status_code == 200:
   
        return response.json() # Return the JSON response
    else:
        print('Error')
        return None
    



#this function will parse the pom.xml file
#Apporch is simple, check if the path in the repository is a file or a folder
#If it is a file, check if the file is a pom.xml file
#If it is a folder, we recursively call the function to get the files in the folder
#the using the xml.etree.ElementTree to parse the xml file

def parser(owner, repo, path='', visited=None):
    # maintaining a set of visited folders
    # to avoid revisiting the same folder
    if visited is None:  
        visited = set()

    path = get_path(owner, repo, path) # Get the path of the files in the repository
    if path is not None:  
        for file in path:
            if file['type'] == 'file':
                # print("File:", file['name'])
                if re.search(r'pom\.xml', file['name'], re.IGNORECASE): # Check if the file is a pom.xml file
                    print("POML file found.")
                    
                    # Set the headers
                    headers = {
                        'Authorization': f"token {os.getenv('ACCESS_TOKEN')}",
                        'Accept': 'application/vnd.github.v3+json'
                    }

                    # Send GET request to the URL
                    content = requests.get(file['download_url'], headers=headers,timeout=5).text
                   

                    # Parse the XML content
                    root = ET.fromstring(content)
                    #check the namespace of the xml file
                    namespace = re.search(r'{.*}', root.tag)
                    namespace = namespace.group(0)

                    # Get the group ID, artifact ID, and version
                    group_id = root.find(f'.//{namespace}groupId').text
                    artifact_id = root.find(f'.//{namespace}artifactId').text
                    version = root.find(f'.//{namespace}version').text
                    print("path:", file['path'])
                    print("Group ID:", group_id)
                    print("Artifact ID:", artifact_id)
                    print("Version:", version)
                    print()
            else:
                #get the path of the folder
                full_path = file['path']
                # check if the folder has been visited
                if file['name'] not in visited:
                    
                    visited.add(file['name']) # Add the folder to the set of visited folders
                    parser(owner, repo, full_path, visited) # Recursively call the function to get the files in the folder
    else:
        print("No files found")


# start = time.time()
# parser('shopizer-ecommerce', 'shopizer', '')
# end = time.time()
# print(end - start)

def main():
    input_owner = input("Enter the owner of the repository: ")
    input_repo = input("Enter the name of the repository: ")
    start   = time.time()
    repo_list_names = repoList(input_owner)
    print(repo_list_names)
    # input_repo =random.choice(repo_list_names)
    print(input_repo)
    parser(input_owner, input_repo, '')
    end = time.time()
    print(end - start)



if __name__ == "__main__":
    main()





# refernces: 
# https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api?apiVersion=2022-11-28
# https://stackoverflow.com/questions/70026376/how-can-i-use-the-github-rest-api-to-access-a-files-data-in-a-private-repositor
# https://docs.python.org/3/library/xml.etree.elementtree.html
# https://www.datacamp.com/tutorial/python-xml-elementtree
