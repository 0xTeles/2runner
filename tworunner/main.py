import base64
import io
import json
import sys
import time
import uuid
from zipfile import ZipFile

import httpx


def get_user(token):
    r = httpx.get(
        'https://api.github.com/user',
        headers={'Authorization': f'Bearer {token}'},
    )
    data = json.loads(r.text)

    try:
        return data['login']
    except Exception:
        return False


def create_repository(hash, token):
    r = httpx.post(
        'https://api.github.com/user/repos',
        data=json.dumps({
            'name': hash,
            'description': 'temp repo from 2runner',
            'private': True,
        }),
        headers={'Authorization': f'Bearer {token}'},
    )
    if r.status_code == httpx.codes.CREATED:
        return hash
    else:
        return False


def send_content(repo, owner, content, token, filename):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json',
    }

    encoded_content = base64.b64encode(content.encode()).decode('utf-8')

    body = json.dumps({
        'message': 'Add EXAMPLE file',
        'committer': {'name': '2runner', 'email': 'random@random.com'},
        'content': encoded_content,
    })

    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{filename}'
    r = httpx.put(url, headers=headers, data=body)
    if r.status_code == httpx.codes.CREATED:
        return hash
    else:
        return False


def get_artifact(repo, owner, token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    r = httpx.get(
        f'https://api.github.com/repos/{owner}/{repo}/actions/artifacts',
        headers=headers,
    )
    data = json.loads(r.text)
    if data['total_count'] == 0:
        return False
    else:
        for artifact in data['artifacts']:
            try:
                url = artifact['archive_download_url']
                r = httpx.get(url, headers=headers, follow_redirects=True)
                zipf = io.BytesIO(r.content)
                file = ZipFile(zipf, 'r')
                return file.read('results.txt').decode('utf-8').split('\n')
            except Exception:
                continue
    return False


def del_repository(repo, owner, token):
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    r = httpx.delete(
        f'https://api.github.com/repos/{owner}/{repo}', headers=headers
    )
    if r.status_code == httpx.codes.NO_CONTENT:
        return True
    else:
        return False


def test_http(content):
    url = content.split(' ')

    if len(url) <= 1:
        return

    try:
        r = httpx.get(url[0], verify=False, timeout=3)
        print(
            f'[+] URL -> {url[0]} | GHActions -> {url[1]} | Your Machine -> [{r.status_code}]'
        )
    except Exception:
        print(
            f'[+] URL -> {url[0]} | GHActions -> {url[1]} | Your Machine -> Error'
        )


def runner(tokens, hosts, workflow):
    for token in tokens:
        owner = get_user(token)
        if not owner:
            print('[X] Please, check the token!')
            continue

        repo = uuid.uuid4()
        create_repo = create_repository(str(repo), token)
        if not create_repo:
            print(
                f"[!] Repository in {owner} couldn't been created, check your permissions!!"
            )
            continue
        print(f'[+] Repository in {owner} have been created!')

        create_file = send_content(repo, owner, hosts, token, 'file.txt')
        if not create_file:
            print(
                f"[!] File in {owner}/{repo} couldn't been created, check your permissions!!"
            )
            continue
        print(f'[+] File in {owner}/{repo} have been created!')

        create_workflow = send_content(
            repo, owner, workflow, token, '.github/workflows/check_hosts.yml'
        )
        if not create_workflow:
            print(
                f"[!] Workflow in {owner}/{repo} couldn't been created, check your permissions!!"
            )
            continue
        print(f'[+] Workflow in {owner}/{repo} have been created!')

        status = False
        while status is False:
            print(f'[+] Status => {status}! Wait... 2 minutes, please')
            time.sleep(30)
            file = get_artifact(repo, owner, token)
            if file:
                for i in file:
                    test_http(i)
                status = True

        delete_repo = del_repository(repo, owner, token)
        if not delete_repo:
            print(
                f"[!] Exclusion of {owner}/{repo} couldn't been created, check your permissions!!"
            )
            sys.exit(0)

        print(
            f'[+] Exclusion of {owner}/{repo} have been success, check your permissions!!'
        )
