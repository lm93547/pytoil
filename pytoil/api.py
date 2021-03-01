"""
Module responsible for querying the GitHub RESTv3 API.

Author: Tom Fleet
Created: 04/02/2021
"""

from typing import Any, Dict, List, Optional, Union

import httpx

from .config import Config

# Type hint for generic JSON API response
# either a single JSON blob or a list of JSON blobs
RepoBlob = Dict[str, Any]
APIResponse = Any


class API:
    def __init__(
        self, token: Optional[str] = None, username: Optional[str] = None
    ) -> None:
        """
        Representation of the GitHub API.

        Args:
            token (Optional[str], optional): GitHub Personal Access Token.
                Defaults to value from config file.

            username (Optional[str], optional): Users GitHub username.
                Defaults to value from config file.
        """
        # If token passed, set it
        # if not, get from config
        self._token = token or Config.get().token
        # If username passed, set it
        # if not, get from config
        self._username = username or Config.get().username

        self.baseurl: str = "https://api.github.com/"

        self._headers: Dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {self._token}",
        }

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(token={self._token!r}, "
            + f"username={self.username!r})"
        )

    @property
    def token(self) -> Union[str, None]:
        return self._token

    @token.setter
    def token(self, value: str) -> None:
        self._token = value

    @property
    def username(self) -> Union[str, None]:
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        self._username = value

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @headers.setter
    def headers(self, value: Dict[str, str]) -> None:
        """
        Incase we ever need to set headers explictly.
        """
        self._headers = value

    def get(self, endpoint: str) -> APIResponse:
        """
        Makes an authenticated request to a GitHub API endpoint
        e.g. 'users/repos'.

        Generic base for more specific get methods below.

        Args:
            endpoint (str): Valid GitHub API endpoint.

        Raises:
            APIRequestError: If any HTTP error occurs, will raise an exception
                and give a description and standard HTTP status code.

        Returns:
            ApiResponse: JSON API response.
        """
        # This needs the token from the config
        Config.get().raise_if_unset()

        r = httpx.get(url=self.baseurl + endpoint, headers=self.headers)
        r.raise_for_status()
        response: APIResponse = r.json()

        return response

    def get_repo(self, repo: str) -> APIResponse:
        """
        Hits the GitHub REST API 'repos/{owner}/{repo}' endpoint
        and parses the response.

        In other words it gets the JSON representing a particular `repo`
        belonging to `username`.

        Args:
            repo (str): The name of the repo to fetch JSON for.

        Returns:
            APIResponse: JSON response for a particular repo.
        """

        return self.get(f"repos/{self.username}/{repo}")

    def get_repos(self) -> APIResponse:
        """
        Hits the GitHub REST API 'user/{username}/repos' endpoint and parses
        the response.

        Function similar to `get_repo` the difference being `get_repos` returns
        a list of JSON blobs each representing a repo belonging to `self.username`

        This endpoint requires no parameters because it is the
        'get repos for authenticated user' endpoint and since at this point we have
        `self.token` this automatically fills in the {username} for us.

        Returns:
            APIResponse: JSON response for a list of all users repos.
        """

        # Because the user is authenticated (token)
        # This gets their repos
        # get will raise if missing token
        return self.get("user/repos")

    def get_repo_names(self) -> List[str]:
        """
        Hits the GitHub REST API 'user/{username}/repos' endpoint, parses
        the response, extracts the name of each repo and returns
        a list of these names.

        Returns:
            List[str]: List of user's repo names.
        """

        raw_repo_data = self.get_repos()

        names = [repo["name"] for repo in raw_repo_data]

        return names

    def get_repo_info(self, repo: str) -> Dict[str, Union[str, int]]:
        """
        Returns a dictionary of key information about a particular repo.

        Info Keys:
        - name
        - description
        - created_at
        - updated_at
        - size
        - license

        Args:
            repo (str): Name of the repo to get info for.

        Returns:
            Dict[str, Union[str, int]]: Dict of repo information.
        """

        raw_repo_data = self.get_repo(repo=repo)

        keys_to_get: List[str] = [
            "name",
            "description",
            "created_at",
            "updated_at",
            "size",
            "license",
        ]

        display_dict: Dict[str, Union[str, int]] = {
            key: raw_repo_data.get(key, "Not Found") for key in keys_to_get
        }

        # License is itself a dict
        # Couldn't be bothered doing some clever recursive thing for one key
        display_dict["license"] = raw_repo_data.get("license", "Not Found").get(
            "name", "Not Found"
        )

        return display_dict