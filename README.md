# Decision Records

This repository is intended as a place to collect architectural / technical decisions.

Those may be in the form of "Any Decision Records" (ADR), protocols or images.
Images must be accompanied by a text file with a matching name that explains its context, references etc.

Please be aware that the information here is public and that this repository may be synchronized to Github.

For records about internal decisions see the private repository [univention/internal/decision-records](https://git.knut.univention.de/univention/internal/decision-records).

## Directory structure

- Top level directories should be products or concerns, not teams.
- Cross-cutting concerns (e.g. logging, security, deployment) may be found at higher levels than affected software.
- Please do not add more than one level of subdirectories.
- Here is an [example directory structure](example-dirs.md). It's just an example - you and your team know best.

## Editing

- For new ADRs, please use [`adr-template.md`](adr-template.md) as basis.
- We are implementing ADR in the form of [Markdown Any Decision Records (MADR)](https://adr.github.io/madr/).
- Please use Markdown files and a format that renders well in Gitlab: [CommonMark](https://commonmark.org/help/) or [GitLab Flavored Markdown](https://docs.gitlab.com/ee/user/markdown.html).
- A well established process for adding an ADR is:
  - Create a branch.
  - Copy the [template](adr-template.md).
  - Adapt the contents. In the metadata at the top set `status: proposed`.
  - Create a merge request (MR) and invite your team via email and in the daily to comment on the MR.
  - When all discussion threads are resolved (or nobody has commented for a week), send an email with a deadline.
  - When the deadline expires without a veto the ADR is `status: accepted` and you can merge the branch into `main`.

---

Please install `pre-commit` before committing to this repository:

```shell
pip install pre-commit
pre-commit install --install-hooks
pre-commit run -a
```
