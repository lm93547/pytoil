"""
CLI sync command.

Author: Tom Fleet
Created: 28/02/2021
"""

from typing import List, Set

import typer

from pytoil.api import API
from pytoil.config import Config
from pytoil.repo import Repo

app = typer.Typer(no_args_is_help=True)


# Callback for documentation only.
@app.callback()
def sync() -> None:
    """
    Synchronise your local and remote projects.

    sync is a safe method in that existing local
    projects will not be modified in any way.
    """


# Can't call it all, keyword!
@app.command(name="all")
def all_(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force sync without confirmation prompt.",
        show_default=False,
    )
) -> None:
    """
    Pull down all your remote projects that don't already
    exist.

    Will not operate on or modify in any way the projects that
    already exist.

    Example

    $ pytoil sync all

    $ pytoil sync all --force
    """

    # Everything below requires a valid config
    config = Config.get()
    config.raise_if_unset()

    api = API()

    local_projects: Set[str] = {
        f.name
        for f in config.projects_dir.iterdir()
        if f.is_dir() and not f.name.startswith(".")
    }

    remote_projects: Set[str] = set(api.get_repo_names())

    to_clone: Set[str] = remote_projects.difference(local_projects)

    if len(to_clone) == 0:
        typer.secho(
            "\nAll your remote repos already exist locally. Nothing to do.",
            fg=typer.colors.GREEN,
        )
    else:
        if not force:
            typer.confirm(
                f"This will clone {len(to_clone)} repos."
                + " Are you sure you want to proceed?",
                abort=True,
            )

            # If user said no, typer will abort and the following will not run
            # If they said yes, it will run
            typer.echo("You said yes")
            for repo_name in to_clone:
                # Create the repo object and clone
                repo = Repo(name=repo_name)
                typer.echo("\nCloning: {repo.name!r}.")
                repo.clone()

        else:
            # User said force, so just go and do it
            for repo_name in to_clone:
                # Create the repo object and clone
                repo = Repo(name=repo_name)
                typer.echo("\nCloning: {repo.name!r}.")
                repo.clone()


@app.command()
def these(
    repos: List[str] = typer.Argument(..., help="List of remote repos to pull down."),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force sync without confirmation prompt.",
        show_default=False,
    ),
) -> None:
    """
    Only pull down specified remote projects.

    Any projects in the list that already exist locally
    will be skipped and will not be modified in any way.

    Examples

    $ pytoil sync these project1 project2 project3

    $ pytoil sync these --force project1 project2
    """

    # Everything below requires a valid config
    config = Config.get()
    config.raise_if_unset()

    local_projects: Set[str] = {
        f.name
        for f in config.projects_dir.iterdir()
        if f.is_dir() and not f.name.startswith(".")
    }

    # Accept a list of repos from the user
    remote_projects: Set[str] = set(repos)

    to_clone: Set[str] = remote_projects.difference(local_projects)

    if len(to_clone) == 0:
        typer.secho(
            "\nAll your remote repos already exist locally. Nothing to do.",
            fg=typer.colors.GREEN,
        )
    else:
        if not force:
            typer.confirm(
                f"This will clone {len(to_clone)} repos."
                + " Are you sure you want to proceed?",
                abort=True,
            )

            # If user said no, typer will abort and the following will not run
            # If they said yes, it will run
            typer.echo("You said yes")
            for repo_name in to_clone:
                # Create the repo object and clone
                repo = Repo(name=repo_name)
                typer.echo("\nCloning: {repo.name!r}.")
                repo.clone()

        else:
            # User said force, so just go and do it
            for repo_name in to_clone:
                # Create the repo object and clone
                repo = Repo(name=repo_name)
                typer.echo("\nCloning: {repo.name!r}.")
                repo.clone()