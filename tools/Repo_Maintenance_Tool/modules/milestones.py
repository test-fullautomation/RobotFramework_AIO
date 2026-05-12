import logging
import requests
from urllib.parse import quote

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


def _headers(token: str) -> dict:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }


def _find_milestone(repo: str, token: str, name: str, state: str = "open") -> dict | None:
    """Find a milestone by name. Returns the milestone dict or None."""
    url = f"{GITHUB_API}/repos/{repo}/milestones"
    page = 1
    while True:
        resp = requests.get(url, headers=_headers(token), params={"state": state, "per_page": 100, "page": page})
        if resp.status_code != 200:
            logger.error("Failed to fetch milestones from %s – %s: %s", repo, resp.status_code, resp.text)
            return None
        batch = resp.json()
        if not batch:
            break
        for ms in batch:
            if ms["title"] == name:
                return ms
        page += 1
    return None


def create_milestone(repo: str, token: str, name: str, description: str | None = None,
                     due_date: str | None = None) -> bool:
    """Create a milestone if it does not already exist.

    Args:
        repo: Full repo name, e.g. 'owner/repo'.
        token: GitHub PAT.
        name: Milestone title.
        description: Optional milestone description.
        due_date: Due date in ISO 8601 format (YYYY-MM-DDT00:00:00Z) or None.

    Returns:
        True if created or already exists, False on error.
    """
    logger.debug("Checking if milestone '%s' exists in %s", name, repo)
    existing = _find_milestone(repo, token, name)
    if existing is not None:
        logger.info("Milestone '%s' already exists in %s (number %d) – skipping.", name, repo, existing["number"])
        return True

    url = f"{GITHUB_API}/repos/{repo}/milestones"
    payload: dict = {"title": name}
    if description is not None:
        payload["description"] = description
    if due_date is not None:
        payload["due_on"] = due_date

    logger.debug("Creating milestone '%s' in %s (due: %s)", name, repo, due_date or "none")
    resp = requests.post(url, headers=_headers(token), json=payload)

    if resp.status_code == 201:
        logger.info("Milestone '%s' created successfully in %s.", name, repo)
        return True

    logger.error("Failed to create milestone '%s' in %s – %s: %s", name, repo, resp.status_code, resp.text)
    return False


def close_milestone(repo: str, token: str, name: str) -> bool:
    """Close an open milestone by name.

    Args:
        repo: Full repo name.
        token: GitHub PAT.
        name: Milestone title.

    Returns:
        True if closed, False on error.
    """
    logger.debug("Looking for open milestone '%s' in %s", name, repo)
    ms = _find_milestone(repo, token, name, state="open")
    if ms is None:
        logger.warning("Milestone '%s' not found (open) in %s – cannot close.", name, repo)
        return False

    url = f"{GITHUB_API}/repos/{repo}/milestones/{ms['number']}"
    resp = requests.patch(url, headers=_headers(token), json={"state": "closed"})

    if resp.status_code == 200:
        logger.info("Milestone '%s' (number %d) closed in %s.", name, ms["number"], repo)
        return True

    logger.error("Failed to close milestone '%s' in %s – %s: %s", name, repo, resp.status_code, resp.text)
    return False


def delete_milestone(repo: str, token: str, name: str) -> bool:
    """Delete a milestone by name.

    Args:
        repo: Full repo name.
        token: GitHub PAT.
        name: Milestone title.

    Returns:
        True if deleted, False on error.
    """
    ms = _find_milestone(repo, token, name)
    if ms is None:
        ms = _find_milestone(repo, token, name, state="closed")
    if ms is None:
        logger.warning("Milestone '%s' not found in %s – nothing to delete.", name, repo)
        return False

    url = f"{GITHUB_API}/repos/{repo}/milestones/{ms['number']}"
    resp = requests.delete(url, headers=_headers(token))

    if resp.status_code == 204:
        logger.info("Milestone '%s' (number %d) deleted from %s.", name, ms["number"], repo)
        return True

    logger.error("Failed to delete milestone '%s' in %s – %s: %s", name, repo, resp.status_code, resp.text)
    return False


def update_milestone_due_date(repo: str, token: str, name: str, due_date: str | None) -> bool:
    """Change the due date of a milestone.

    Args:
        repo: Full repo name.
        token: GitHub PAT.
        name: Milestone title.
        due_date: New due date in ISO 8601 format, or None to clear.

    Returns:
        True if updated, False on error.
    """
    ms = _find_milestone(repo, token, name)
    if ms is None:
        logger.warning("Milestone '%s' not found in %s.", name, repo)
        return False

    url = f"{GITHUB_API}/repos/{repo}/milestones/{ms['number']}"
    payload: dict = {"due_on": due_date}
    resp = requests.patch(url, headers=_headers(token), json=payload)

    if resp.status_code == 200:
        logger.info("Milestone '%s' due date updated to %s in %s.", name, due_date or "none", repo)
        return True

    logger.error("Failed to update due date for '%s' in %s – %s: %s", name, repo, resp.status_code, resp.text)
    return False


def update_milestone_description(repo: str, token: str, name: str, description: str) -> bool:
    """Change the description of a milestone.

    Args:
        repo: Full repo name.
        token: GitHub PAT.
        name: Milestone title.
        description: New description text.

    Returns:
        True if updated, False on error.
    """
    ms = _find_milestone(repo, token, name)
    if ms is None:
        logger.warning("Milestone '%s' not found in %s.", name, repo)
        return False

    url = f"{GITHUB_API}/repos/{repo}/milestones/{ms['number']}"
    resp = requests.patch(url, headers=_headers(token), json={"description": description})

    if resp.status_code == 200:
        logger.info("Milestone '%s' description updated in %s.", name, repo)
        return True

    logger.error("Failed to update description for '%s' in %s – %s: %s", name, repo, resp.status_code, resp.text)
    return False