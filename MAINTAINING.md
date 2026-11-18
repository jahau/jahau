# Maintaining the profile README

`README.md` in this repository is shown on the [GitHub profile page](https://github.com/jahau). This file records how it is kept accurate.

## Featured projects

A repository is listed under **Featured Open-Source Projects** only when all of the following are true:

- it is an original repository, not a fork, and it is public
- it has a published (non-draft) GitHub Release
- its README documents installation and usage, with an example or demo
- it has a license file

Planned or unreleased repositories are not listed. Each row uses dynamic [shields.io](https://shields.io) badges for the latest release and the star count; star counts and release numbers are never written by hand.

Forks are not featured. The README links to the [original repositories](https://github.com/jahau?tab=repositories&type=source) and [forks](https://github.com/jahau?tab=repositories&type=fork) filters so the two stay distinguishable.

Achievements, statistics, or other claims are added only when they can be verified from a public source.

## Updating

1. Check the candidate repository against the criteria above, for example:

   ```console
   gh repo view jahau/<repo> --json isFork,visibility,licenseInfo,latestRelease
   gh release view -R jahau/<repo>
   ```

2. Add or change the table row on a feature branch and open a pull request.
3. Run the check locally:

   ```console
   python scripts/check_readme.py README.md MAINTAINING.md
   ```

## Validation

[`scripts/check_readme.py`](scripts/check_readme.py) (Python standard library only) checks that:

- every Markdown table row has the same number of columns as its header
- relative links point to existing files
- external links and images return a non-error HTTP status, and `http://` links are flagged
- shields.io GitHub badges refer to a repository that exists, because shields.io renders an image even for a missing repository

`--offline` skips the network checks. The [README check workflow](.github/workflows/readme-check.yml) runs it on every push and pull request and weekly, to catch links that break later.

## Pinned repositories

Pinned repositories are chosen in the GitHub web UI (**Customize your pins** on the profile page). They cannot be set from this repository, so changes there are a manual step and are not part of a pull request.

Recommended six pins, original projects with published releases:

1. [workflow-trust-check](https://github.com/jahau/workflow-trust-check)
2. [agent-permission-map](https://github.com/jahau/agent-permission-map)
3. [agent-session-diff](https://github.com/jahau/agent-session-diff)
4. [ai-repo-rules-generator](https://github.com/jahau/ai-repo-rules-generator)
5. [wp-security-doctor](https://github.com/jahau/wp-security-doctor)
6. [github-contribution-doctor](https://github.com/jahau/github-contribution-doctor)
