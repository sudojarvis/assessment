import requests
import re
import time
import xml.etree.ElementTree as ET
import random
import os
from dotenv import load_dotenv

load_dotenv()


import requests

def authenticate_with_github(client_id, client_secret):

    # Obtaining the authorization code
    auth_url = 'https://github.com/login/oauth/authorize'
    params = {
        'client_id': client_id,
        'scope': 'repo',  
    }
    response = requests.get(auth_url, params=params)
    print("Please visit this URL and authorize the application:", response.url)

    #example of the authorization code
    # https://github.com/sudojarvis?code=0b5e2644c4054eb0c226
    # 0b5e2644c4054eb0c226 is the authorization code


    authorization_code = input("Enter the authorization code: ")
    #--------------------------------------------------------------------


    # Exchanging the authorization code for an access token
    token_url = 'https://github.com/login/oauth/access_token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': authorization_code,
    }
    headers = {
        'Accept': 'application/json',
    }

    # Send POST request to the URL
    response = requests.post(token_url, data=data, headers=headers)
    access_token = response.json().get('access_token')

    # Check if the access token was obtained
    if access_token:
        print("Successfully authenticated with GitHub!")
        return access_token
    else:
        print("Authentication failed.")
        return None





#this function will get the list of repositories
def repoList(access_token, owner='user'):

    if access_token:
        # Set the headers
        headers = { 'Authorization': f'token {access_token}',
                    'Accept': 'application/vnd.github.v3+json'}
                   
        # response = requests.get('https://api.github.com/user/repos', headers=headers)
        response = requests.get(f'https://api.github.com/users/{owner}/repos', headers=headers) # Send GET request to the URL
        if response.status_code == 200:
            repo_list = []
            for repo in response.json():
                repo_list.append(repo['name'])
            return repo_list
        else:
            print('Error')
            return None
    else:
        print("Authentication failed.")
        return None
 




#this function will get the path of folders and files in the repository
def get_path(access_token, owner, repository, path=''):
    
   
    # Set the headers
    headers = { 'Authorization': f'token {access_token}',
            'Accept': 'application/vnd.github.v3+json'}
            

    url = f"https://api.github.com/repos/{owner}/{repository}/contents/{path}" # f-strings to insert the owner, repository, and path into the URL

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

def parser(access_token, owner, repo, path='', visited=None):
    # maintaining a set of visited folders
    # to avoid revisiting the same folder
    if visited is None:  
        visited = set()

    path = get_path(owner=owner, repository=repo, path=path, access_token=access_token) # Get the files in the repository
    if path is not None:  
        for file in path:
            if file['type'] == 'file':
                # print("File:", file['name'])
                if re.search(r'pom\.xml', file['name'], re.IGNORECASE): # Check if the file is a pom.xml file
                    print("POML file found.")
                    
                    # Set the headers
                    headers = {
                        'Authorization': f"token {access_token}", # f-strings to insert the access token into the header
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
                    parser(access_token, owner, repo, full_path, visited) # Recursively call the function to get the files in the folder
    else:
        print("No files found")



        
# this is the main function that will call the other functions
def main():

    start   = time.time()
    # reading the client_id and client_secret from the .env file
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')

    #authenticate with github and get the access token
    access_token = authenticate_with_github(client_id, client_secret)
    print("-------------------------------")
    if access_token:
        print("Authentication successful. Access token:", access_token)
    else:
        print("Authentication failed.")
    print("-------------------------------")


    #this is the owner of the repository
    input_owner = 'shopizer-ecommerce'

    #get the list of repositories
    repo_list_names = repoList( access_token, owner=input_owner)
    print(repo_list_names)
    print("-------------------------------")

    #select the repository to parse from the list of repositories
    input_repo = input("Select the repository to parse: ")
    print("-------------------------------")

    #parse the repository
    parser(access_token, input_owner, input_repo, '')

    end = time.time()
    print(end - start)



if __name__ == "__main__":
    main()





