import re
import requests

REPO = "test-fullautomation/robotframework_aio_website"
API_URL = f"https://api.github.com/repos/{REPO}/labels"

NEW_LABEL = "0.15.1"
RED = "e11d48"
BLUE = "1d4ed8"

VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def main():
    token = input("Enter your GitHub Personal Access Token: ").strip()
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    # 1. Get existing labels
    labels = []
    page = 1
    while True:
        resp = requests.get(API_URL, headers=headers, params={"per_page": 100, "page": page})
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        labels.extend(data)
        page += 1

    version_labels = [l for l in labels if VERSION_PATTERN.match(l["name"])]
    print(f"Found version labels: {[l['name'] for l in version_labels]}")

    # 2. Create new label "0.15.1" in red
    if any(l["name"] == NEW_LABEL for l in version_labels):
        print(f"Label '{NEW_LABEL}' already exists, updating color to red.")
        resp = requests.patch(f"{API_URL}/{NEW_LABEL}", headers=headers, json={"color": RED})
        resp.raise_for_status()
    else:
        print(f"Creating label '{NEW_LABEL}' in red.")
        resp = requests.post(API_URL, headers=headers, json={"name": NEW_LABEL, "color": RED})
        resp.raise_for_status()

    # 3. Update older version labels to blue
    for label in version_labels:
        if label["name"] == NEW_LABEL:
            continue
        if label["color"].lower() != BLUE:
            print(f"Updating label '{label['name']}' to blue.")
            resp = requests.patch(f"{API_URL}/{label['name']}", headers=headers, json={"color": BLUE})
            resp.raise_for_status()

    print("Done!")


if __name__ == "__main__":
    main()