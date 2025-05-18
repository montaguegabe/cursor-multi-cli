#!/usr/bin/env python3

import logging

import click

from cursor_multi.git_helpers import get_current_branch, run_git
from cursor_multi.ignore_files import (
    update_gitignore_with_repos,
    update_ignore_with_repos,
)
from cursor_multi.merge_cursor import import_cursor_rules
from cursor_multi.merge_vscode import merge_vscode_configs
from cursor_multi.paths import paths
from cursor_multi.repos import load_repos

logger = logging.getLogger(__name__)


def clone_repos():
    """Clone all repositories from the repos.json file."""
    repos = load_repos()

    # Get the current branch of the parent repo
    current_branch = get_current_branch(paths.root_dir)
    logger.info(f"📌 Current branch: {current_branch}")

    for repo in repos:
        if repo.path.exists():
            logger.info(f"📁 {repo.name} already exists, skipping...")
            continue

        logger.info(f"\n🔄 Cloning {repo.name}...")

        # First clone the default branch
        run_git(
            ["clone", repo.url, str(repo.path)],
            f"clone {repo.name}",
            paths.root_dir,
        )

        # Then checkout the same branch as parent repo if it exists
        try:
            run_git(
                ["checkout", current_branch],
                f"checkout branch {current_branch}",
                repo.path,
            )
            logger.info(
                f"✅ Successfully cloned {repo.name} and checked out branch {current_branch}"
            )
        except SystemExit:
            logger.warning(
                f"Branch {current_branch} not found in {repo.name}, staying on default branch"
            )

    update_gitignore_with_repos()
    update_ignore_with_repos()


def sync():
    logger.info("🚀 Syncing development environment...")

    clone_repos()
    import_cursor_rules()
    merge_vscode_configs()

    logger.info("\n✨ Sync complete!")


@click.command(name="sync")
def sync_cmd():
    """Set up the complete development environment.

    This command will:
    1. Clone all repositories from repos.json
    2. Check out matching branches if they exist
    3. Update .gitignore and other ignore files
    4. Import Cursor rules from all repositories
    5. Merge VSCode configurations (settings, launch, tasks)
    """
    sync()
