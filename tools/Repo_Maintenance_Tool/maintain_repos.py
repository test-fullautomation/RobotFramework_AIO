#!/usr/bin/env python3
"""GitHub Repository Maintenance Tool.

Maintains GitHub repositories by managing labels, milestones, and more.
Configuration is read from JSON files in the config/ directory.
"""

import argparse
import getpass
import json
import logging
import sys
import re
from pathlib import Path

from modules.labels import create_label, change_label_color, delete_label
from modules.milestones import (create_milestone, close_milestone,
                                delete_milestone, update_milestone_due_date,
                                update_milestone_description)

CONFIG_DIR = Path(__file__).parent / "config"

VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)-7s] %(name)s – %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_json(filename: str) -> dict:
    filepath = CONFIG_DIR / filename
    logging.debug("Loading config from %s", filepath)
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="GitHub Repository Maintenance Tool")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose/debug logging")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)
    logger = logging.getLogger("main")

    # --- Load configuration ---
    repos_cfg = load_json("repos.json")
    labels_cfg = load_json("labels.json")

    # --- PAT ---
    token = repos_cfg.get("token", "").strip()
    if not token:
        token = getpass.getpass("GitHub Personal Access Token (PAT): ").strip()
    if not token:
        logger.error("No PAT provided – aborting.")
        sys.exit(1)

    repos: list[str] = repos_cfg.get("repos", [])
    labels: list[dict] = labels_cfg.get("labels", [])
    color_aliases: dict[str, str] = labels_cfg.get("color_aliases", {})

    if not repos:
        logger.error("No repositories configured in config/repos.json.")
        sys.exit(1)

    # --- Process each repo ---
    for repo in repos:
        logger.info("=" * 60)
        logger.info("Processing repository: %s", repo)
        logger.info("=" * 60)


        logger.info("--- Labels: Changing color version label to 'inactive'  ---")
        change_label_color(repo, token, VERSION_PATTERN, "col_version_inactive", color_aliases=color_aliases)

        logger.info("--- Labels: adding 'active' 0.15.1, 'inactive' 0.15.2 1.0.0 1.0.1  ---")
        create_label(repo, token, "0.15.1", "col_version_active", color_aliases=color_aliases)
        create_label(repo, token, "0.15.2", "col_version_inactive", color_aliases=color_aliases)
        create_label(repo, token, "1.0.0", "col_version_inactive", color_aliases=color_aliases)
        create_label(repo, token, "1.0.1", "col_version_inactive", color_aliases=color_aliases)
        change_label_color(repo, token, "0.15.1", "col_version_active", color_aliases=color_aliases)

        logger.info("--- Milestones: closing 0.14.2,0.14.3,0.14.4,0.14.5,0.15.0 ---")
        close_milestone(repo, token, "0.14.2")
        close_milestone(repo, token, "0.14.3")
        close_milestone(repo, token, "0.14.4")
        close_milestone(repo, token, "0.14.5")
        close_milestone(repo, token, "0.15.0")

        logger.info("--- Milestones: creating 0.15.1 0.15.2 1.0.0 1.0.1 ---")
        create_milestone(repo, token, "0.15.1", "RobotFramework AIO 0.15.1", None)
        create_milestone(repo, token, "0.15.2", "RobotFramework AIO 0.15.2", None)
        create_milestone(repo, token, "1.0.0", "RobotFramework AIO 1.0.0", None)
        create_milestone(repo, token, "1.0.1", "RobotFramework AIO 1.0.1", None)



        # 1. Create labels (color aliases resolved inside module)
        #logger.info("--- Label maintenance ---")
        #for lbl in labels:
        #create_label(repo, token, "testlabel", "orange", color_aliases=color_aliases)
        #delete_label(repo, token, "testlabel")

        # 2. Change color of labels matching a pattern (example, using alias)
        
        # 3. Create milestones (example)
        #logger.info("--- Milestone maintenance ---")
        #create_milestone(repo, token, "v1.0.0", due_date="2025-12-31T00:00:00Z")
        #create_milestone(repo, token, "v1.1.0", "description1", due_date=None)
        #update_milestone_description(repo, token, "v1.1.0", "description2")
        #update_milestone_due_date(repo, token, "v1.1.0", None)
        #delete_milestone(repo, token, "v1.1.0")
        # 4. Close a milestone (example)
        #logger.info("--- Closing milestone '0.14.5' ---")
        #close_milestone(repo, token, "0.14.5")

    logger.info("Done.")


if __name__ == "__main__":
    main()