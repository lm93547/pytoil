import asyncio
import sys
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pytoil.environments import Requirements


def test_requirements():
    env = Requirements(root=Path("somewhere"))

    assert env.project_path == Path("somewhere").resolve()
    assert env.name == "requirements file"
    assert env.executable == Path("somewhere").resolve().joinpath(".venv/bin/python")


def test_requirements_repr():
    env = Requirements(root=Path("somewhere"))
    assert repr(env) == f"Requirements(root={Path('somewhere')!r})"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
async def test_install_self_venv_exists(
    mocker: MockerFixture, silent: bool, stdout, stderr
):
    mocker.patch(
        "pytoil.environments.reqs.Requirements.exists",
        autospec=True,
        return_value=True,
    )

    mock = mocker.patch(
        "pytoil.environments.reqs.asyncio.create_subprocess_exec", autospec=True
    )

    env = Requirements(root=Path("somewhere"))

    await env.install_self(silent=silent)

    mock.assert_called_once_with(
        f"{env.executable}",
        "-m",
        "pip",
        "install",
        "-r",
        "requirements.txt",
        cwd=env.project_path,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
async def test_install_self_venv_doesnt_exist(
    mocker: MockerFixture, silent: bool, stdout, stderr
):
    mocker.patch(
        "pytoil.environments.reqs.Requirements.exists",
        autospec=True,
        return_value=False,
    )

    mock = mocker.patch(
        "pytoil.environments.reqs.asyncio.create_subprocess_exec", autospec=True
    )

    mock_create = mocker.patch(
        "pytoil.environments.reqs.Requirements.create", autospec=True
    )

    env = Requirements(root=Path("somewhere"))

    await env.install_self(silent=silent)

    mock_create.assert_called_once()

    mock.assert_called_once_with(
        f"{env.executable}",
        "-m",
        "pip",
        "install",
        "-r",
        "requirements.txt",
        cwd=env.project_path,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
async def test_install_self_requirements_dev(
    mocker: MockerFixture, silent: bool, stdout, stderr
):
    mocker.patch(
        "pytoil.environments.reqs.Requirements.exists",
        autospec=True,
        return_value=True,
    )

    # Make it think that requirements-dev.txt exists
    mocker.patch(
        "pytoil.environments.reqs.aiofiles.os.path.exists",
        autospec=True,
        return_value=True,
    )

    mock = mocker.patch(
        "pytoil.environments.reqs.asyncio.create_subprocess_exec", autospec=True
    )

    env = Requirements(root=Path("somewhere"))

    await env.install_self(silent=silent)

    mock.assert_called_once_with(
        f"{env.executable}",
        "-m",
        "pip",
        "install",
        "-r",
        "requirements-dev.txt",
        cwd=env.project_path,
        stdout=stdout,
        stderr=stderr,
    )
