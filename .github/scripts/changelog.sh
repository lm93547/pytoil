#!/usr/bin/env bash

# Generates the Changelog body for GitHub Releases made by the CI workflow

set -e

current_tag="${GITHUB_REF#refs/tags/}"
start_ref="HEAD"

# Find the previous release on the same branch, skipping prereleases if the
# current tag is a full release
previous_tag=""
while [[ -z $previous_tag || ($previous_tag == *-* && $current_tag != *-*) ]]; do
    previous_tag="$(git describe --tags "$start_ref"^ --abbrev=0)"
    start_ref="$previous_tag"
done

printf "# Changelog\n\n"

git log "$previous_tag".. --merges --oneline --grep='Merge pull request #' |
    while read -r sha title; do
        pr_num="$(grep -o '#[[:digit:]]\+' <<<"$title")"
        pr_desc="$(git show -s --format=%b "$sha" | sed -n '1,/^$/p' | tr $'\n' ' ')"
        printf "* %s %s\n\n" "$pr_desc" "$pr_num"
    done
