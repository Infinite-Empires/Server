EXTENSION = ".res"

import sys, os
import urllib.request
import requests

game_version = sys.argv[1]
counter = 0

def download(url: str, outpath: str, *, version: str | None = None) -> None:
    global counter
    print(f'Fetching "{outpath}"{"" if version is None else f" version {version}"}...')
    urllib.request.urlretrieve(url, outpath)
    counter += 1

def processfile(file: str) -> None:
    if file[-len(EXTENSION):] != EXTENSION: return
    generates = file[:-len(EXTENSION)]
    if game_version == "clear":
        if not os.path.isfile(generates): return
        print(f"Removing {generates}...")
        os.remove(generates)
        global counter
        counter += 1
        return
    with open(file) as f:
        type, value = f.read().strip().split(' ')
        match type:
            case "url":
                download(value.format(version=game_version), generates)
            case "modrinth":
                url = f'https://api.modrinth.com/v2/project/{value}/version?loaders=["fabric"]&game_versions=["{game_version}"]'
                response = requests.get(url)
                if response.status_code != 200:
                    raise ValueError(f'"{url}" responded with a {response.status_code}!')
                versions = response.json()
                newest_version = versions[0] # apparently
                for file in newest_version["files"]:
                    if not file["primary"]: continue
                    download(file["url"], generates, version=newest_version["version_number"])
                    break
            case unknown:
                raise ValueError(f"Unknown Source {unknown}!")

for file in os.listdir():
    processfile(file)
for file in os.listdir("./mods"):
    processfile(os.path.join("mods", file))

print(f"Processed {counter} files!")
