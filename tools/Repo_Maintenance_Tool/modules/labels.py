import re
import logging
import requests
from urllib.parse import quote

logger = logging.getLogger(__name__)

VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

GITHUB_API = "https://api.github.com"


def resolve_color(color: str, color_aliases: dict[str, str] | None = None) -> str:
    """Resolve a color alias to a hex code. If not found, return as-is."""
    if color_aliases and color in color_aliases:
        resolved = color_aliases[color]
        logger.debug("Resolved color alias '%s' -> '#%s'", color, resolved)
        return resolved.lstrip("#")
    return color.lstrip("#")


def _headers(token: str) -> dict:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }


def create_label(repo: str, token: str, name: str, color: str,
                 color_aliases: dict[str, str] | None = None) -> bool:
    """Create a label if it does not already exist.

    Args:
        repo: Full repo name, e.g. 'owner/repo'.
        token: GitHub PAT.
        name: Label name.
        color: Label color alias or hex code.
        color_aliases: Optional alias-to-hex mapping.

    Returns:
        True if created or already exists, False on error.
    """
    color = resolve_color(color, color_aliases)
    url = f"{GITHUB_API}/repos/{repo}/labels/{quote(name, safe='')}"
    logger.debug("Checking if label '%s' exists in %s", name, repo)

    resp = requests.get(url, headers=_headers(token))
    if resp.status_code == 200:
        logger.info("Label '%s' already exists in %s – skipping creation.", name, repo)
        return True

    if resp.status_code != 404:
        logger.error("Unexpected status %s when checking label '%s': %s", resp.status_code, name, resp.text)
        return False

    # Label does not exist – create it
    create_url = f"{GITHUB_API}/repos/{repo}/labels"
    payload = {"name": name, "color": color}
    logger.debug("Creating label '%s' with color #%s in %s", name, color, repo)
    resp = requests.post(create_url, headers=_headers(token), json=payload)

    if resp.status_code == 201:
        logger.info("Label '%s' created successfully in %s.", name, repo)
        return True

    logger.error("Failed to create label '%s' in %s – %s: %s", name, repo, resp.status_code, resp.text)
    return False


def change_label_color(repo: str, token: str, pattern: str, color: str,
                       color_aliases: dict[str, str] | None = None) -> int:
    """Change the color of all labels matching a regex pattern.

    Args:
        repo: Full repo name.
        token: GitHub PAT.
        pattern: Regex pattern to match label names.
        color: Color alias or hex code.
        color_aliases: Optional alias-to-hex mapping.

    Returns:
        Number of labels updated.
    """
    color = resolve_color(color, color_aliases)
    regex = re.compile(pattern)
    url = f"{GITHUB_API}/repos/{repo}/labels"
    logger.debug("Fetching labels from %s to match pattern '%s'", repo, pattern)

    labels = []
    page = 1
    while True:
        resp = requests.get(url, headers=_headers(token), params={"per_page": 100, "page": page})
        if resp.status_code != 200:
            logger.error("Failed to fetch labels from %s – %s: %s", repo, resp.status_code, resp.text)
            return 0
        batch = resp.json()
        if not batch:
            break
        labels.extend(batch)
        page += 1

    updated = 0
    for label in labels:
        if regex.search(label["name"]):
            label_url = f"{GITHUB_API}/repos/{repo}/labels/{quote(label['name'], safe='')}"
            logger.debug("Updating color of label '%s' to #%s", label["name"], color)
            resp = requests.patch(label_url, headers=_headers(token), json={"color": color})
            if resp.status_code == 200:
                logger.info("Label '%s' color updated to #%s in %s.", label["name"], color, repo)
                updated += 1
            else:
                logger.error("Failed to update label '%s' – %s: %s", label["name"], resp.status_code, resp.text)

    logger.info("Updated %d label(s) matching '%s' in %s.", updated, pattern, repo)
    return updated


def delete_label(repo: str, token: str, name: str) -> bool:
    """Delete a label from a repository.

    Args:
        repo: Full repo name, e.g. 'owner/repo'.
        token: GitHub PAT.
        name: Label name to delete.

    Returns:
        True if deleted successfully, False on error.
    """
    url = f"{GITHUB_API}/repos/{repo}/labels/{quote(name, safe='')}"
    logger.debug("Deleting label '%s' from %s", name, repo)

    resp = requests.delete(url, headers=_headers(token))

    if resp.status_code == 204:
        logger.info("Label '%s' deleted successfully from %s.", name, repo)
        return True

    if resp.status_code == 404:
        logger.warning("Label '%s' not found in %s – nothing to delete.", name, repo)
        return False

    logger.error("Failed to delete label '%s' from %s – %s: %s", name, repo, resp.status_code, resp.text)
    return False