import requests, json, base64, io, uuid, time, sys
from zipfile import ZipFile
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

workflow = """
name: Check Hosts with HTTPX

on:
  push:
    branches:
      - main
  workflow_dispatch: 

jobs:
  check_hosts:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    - name: Install HTTPX
      run: |
        sudo apt-get update
        sudo apt-get install -y unzip
        wget https://github.com/projectdiscovery/httpx/releases/download/v1.6.8/httpx_1.6.8_linux_amd64.zip
        unzip httpx_1.6.8_linux_amd64.zip
        sudo mv httpx /usr/local/bin/
    - name: Run HTTPX on Hosts
      run: |
        touch results.txt
        cat file.txt | httpx -status-code -ip -cname -nc -silent -o results.txt
    - name: Upload results as artifact
      uses: actions/upload-artifact@v4
      with:
        name: httpx-results
        path: results.txt
"""

tokens = ["ADD_YOUR_TOKEN"]

hosts = open(sys.argv[1]).read()


def getUser(token):
    headers = {"Authorization":f"Bearer {token}"}
    r = requests.get("https://api.github.com/user", headers=headers)
    data = json.loads(r.text)
    return (data["login"])

def createRepository(hash,token):
    headers = {"Authorization":f"Bearer {token}"}
    body = json.dumps({"name": hash, "description":"temp repo from 2runner", "private":True})
    r = requests.post("https://api.github.com/user/repos", data=body, headers=headers)
    if r.status_code == 201:
        return hash
    else:
        return 1  
def sendContent(repo, owner, content, token, filename):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    encoded_content = base64.b64encode(content.encode()).decode('utf-8')
    
    body = json.dumps({
        "message": "Add EXAMPLE file",
        "committer": {
            "name": "2runner",
            "email": "random@random.com"
        },
        "content": encoded_content
    })
    
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}"
    r = requests.put(url, headers=headers, data=body)
    if r.status_code == 201:
        return hash
    else:
        return 1
def getArtifact(repo, owner, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/actions/artifacts", headers=headers)
    data = json.loads(r.text)
    if (data["total_count"]) == 2:
        url = data["artifacts"][0]["archive_download_url"]
        r = requests.get(url, headers=headers)
        zipf = io.BytesIO(r.content)
        file = ZipFile(zipf, "r")
        return (file.read("results.txt").decode("utf-8").split("\n"))
    else:
        return 1
def deleteRepo(repo, owner, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    r = requests.delete(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
    if r.status_code == 204:
        return 0
    else:
        return 1
def testHTTP(content):
    url = content.split(" ")
    try:
        r = requests.get(url[0], verify=False, timeout=3)
        print(f"[+] URL -> {url[0]} | GHActions -> {url[1]} | Your Machine -> [{r.status_code}]")
    except:
        print(f"[+] URL -> {url[0]} | GHActions -> {url[1]} | Your Machine -> Error")
            
def main():
    for token in tokens:
        owner = getUser(token)
        repo = uuid.uuid4()
        createRepo = createRepository(str(repo), token)
        if createRepo == 1:
            print(f"[!] Repository in {owner} couldn't been created, check your permissions!!")
            continue
        print(f"[+] Repository in {owner} have been created!")
        createWorkflow = sendContent(repo, owner, workflow, token, ".github/workflows/check_hosts.yml")
        if createWorkflow == 1:
            print(f"[!] Workflow in {owner}/{repo} couldn't been created, check your permissions!!")
            continue
        print(f"[+] Workflow in {owner}/{repo} have been created!")
        createFile = sendContent(repo, owner, hosts, token, "file.txt")
        if createFile == 1:
            print(f"[!] File in {owner}/{repo} couldn't been created, check your permissions!!")
            continue
        print(f"[+] File in {owner}/{repo} have been created!")
        status = 0
        while status == 0:
            print(f"[+] Status => {status}! Wait... 2 minutes, please")
            time.sleep(30)
            file = getArtifact(repo,owner,token)
            if file != 1:
                for i in file:
                    testHTTP(i)
                status = 1
        delRepo = deleteRepo(repo, owner, token)
        if delRepo == 1:
            print(f"[!] Exclusion of {owner}/{repo} couldn't been created, check your permissions!!")
            exit(0)
        print(f"[+] Exclusion of {owner}/{repo} have been success, check your permissions!!")

main()
