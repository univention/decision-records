# AGENTS.md

This file provides guidance to coding agents (Claude Code, OpenCode, …)
when working in this repository.

## What this repository is

A collection of architectural and technical decision records for Univention.
There is no application code to build or test —
the deliverables are Markdown documents (plus a few supporting images and scripts).

ADRs follow [MADR](https://adr.github.io/madr/)
("Markdown Any Decision Records"),
customized by [`adr-template.md`](adr-template.md).

**This repository is public and may be synchronized to GitHub.**
Never write customer names, credentials, internal-only URLs,
or unreleased commercial information into a record.
Internal decisions belong in the private
`univention/internal/decision-records` repository.

Exception: `git.knut.univention.de`, and project paths under it, may be named.
Neither the host nor the group structure is a secret,
and evidence drawn from a repository — a code search, a file reference, a commit —
has to stay re-derivable by a reviewer, which needs the real path.
Customer projects are the one part that stays out:
paths under `univention/prof-services/customers/` name a customer,
so report the number of affected projects instead of the path.

## Commands

```shell
# One-time setup (required before committing)
pip install pre-commit
pre-commit install --install-hooks

# Lint everything (the only "test" this repo has; also what CI runs)
pre-commit run -a

# Lint just the file you touched
pre-commit run --files dev/0013-tech-stack-python-http-client.md
```

CI (`.gitlab-ci.yml`) runs nothing but `pre-commit`.
`prek` is a drop-in replacement for `pre-commit` and is used by some developers.
Never bypass the hooks with `--no-verify`.

The only hook is `pymarkdown`, with these rules disabled:
`line-length`, `no-bare-urls`, `no-duplicate-heading`, `no-duplicate-header`,
`no-hard-tabs`, `no-space-in-code`.
Everything else pymarkdown checks is enforced —
most commonly blank lines around headings, lists, and fenced code blocks,
and consistent list indentation.

## Where files go

- Top-level directories are **products or concerns, not teams**
  (`dev/`, `iam/`, `nubus/`, `ucsschool-core/`, `ucsschool-ext/`).
  See [`example-dirs.md`](example-dirs.md).
- At most **one** level of subdirectories.
- Cross-cutting concerns (logging, security, deployment) live at a higher level
  than the software they affect.
- Keep records on the same topic **in one directory**.
  When an ADR supersedes another, they must end up side by side —
  otherwise readers and editors find only one of them
  and miss that it has been superseded.
  If the correct home is a different directory, move the old record there.
- File names: `NNNN-kebab-case-title.md`,
  with `NNNN` a 4-digit sequence number that is **per directory**, not global.
  Check the highest existing number in the target directory before choosing one.
- An image needs an accompanying text file of the same name
  explaining its context and references.

## Workflow for a new or changed ADR

1. Create a branch.
2. Copy [`adr-template.md`](adr-template.md) — always start from the template,
   never from a hand-written skeleton or another ADR.
3. Fill in the content and set the metadata (see below).
   New records start at `status: proposed`.
4. Run `pre-commit run -a`.
5. Open a merge request and invite the team
   (email, and in the daily) to comment on it.
6. When all discussion threads are resolved,
   or nobody has commented for a week,
   send an email with a deadline.
7. When the deadline expires without a veto,
   set `status: accepted` and merge into `main`.

When superseding an existing record,
edit **both** files:
the new one gets `supersedes:`,
the old one gets `superseded by:` and its `status:` updated.

## Metadata fields

The block of `- key: value` lines under the title.
Fill in every field the template lists; use `-` for "not applicable".

- **status** — in practice: `proposed` while under discussion,
  `accepted` once merged after the deadline,
  `superseded` when replaced.
  The template also names `draft`, `submitted to TDA`, and `rejected`.
- **approval level** — `low` | `medium` | `high`.
  **Ask the editor which level they want; never guess or silently default.**
  The three levels are defined in [`approval_level.md`](approval_level.md):
  `low` is decided inside the team(s) and their tech leads;
  `medium` needs the product owner and software architect;
  `high` needs the leadership board.
  The level determines who must be involved *before* the ADR can be accepted,
  so it has to be settled early, not at merge time.
- **source** — the *reason this ADR exists*:
  the ticket, epic, issue, (non-)functional requirement, or PRD
  that led to writing it — most often a link to an epic
  or to an issue in the requirements-management repository.
  If no such artifact exists, write the trigger as a sentence, e.g.
  "Discussions in the dev team and measurements of current and future effort
  led to the strategy change described in this ADR."
  Do not put the chosen solution's documentation here.
- **coordinated with** — everyone involved in the decision
  and whose opinion was sought (subject-matter experts included).
- **scope** — what the record is binding for, and for how long.
  Defaults to the directory the ADR is stored in.
  Set **resubmission** whenever the scope is time-limited.
- **related** — used by some records for non-superseding cross-links;
  optional, not in the template.

Keep `[[_TOC_]]` directly below the metadata block; it is GitLab-specific.

## What belongs in each section

Reviewers in this repository consistently ask for the same structural fixes.
Get these right the first time.

- **Title** — either the solved problem as a statement, optionally including the
  solution, or a topic label. Both forms are allowed.
  Good statement: "Rewrite the Guardian component by keeping only the PDP
  and switching to Cerbos".
  Good topic label: "Tech stack: Python HTTP client library".
  Prefer a statement when the decision has one clear outcome.
  Prefer a topic label when the outcome has several parts that a statement would
  either truncate or inflate into a paragraph — a `Tech stack: …` record that
  picks different tools for different contexts is the usual case.
  Whichever form you use, the title must be **precise enough to identify the record
  on its own, and must not overlap another ADR's title**:
  - List the existing titles before choosing one:
    `grep -m1 -H '^# ' */*.md | sort -t: -k2`.
    Take only each file's *first* `# ` line — a plain `grep '^# '` also matches
    headings inside fenced code blocks, of which this repository has plenty.
    Note that `no-duplicate-heading` is disabled in the lint config,
    so nothing catches a collision for you.
    Two records may legitimately share a title when one supersedes the other —
    `dev/0006-log-format.md` and `dev/0010-log-format.md` are both "Log Format",
    and there the repetition is the point.
    For two *independent* records it is a defect.
  - Disambiguate by naming the language, the side of the wire, or the layer.
    "Python HTTP *client* library" and "Python REST API *server* framework"
    are two records; "HTTP libraries" is neither.
  - Watch for a topic that an existing record already decides part of.
    A new "Python logging" record would collide with ADRs 0004-0010,
    which already decide topology, levels, format and messages —
    name what is actually being chosen, e.g. "Python logging library".
  - Records that belong to a series share a prefix and keep the part after the
    colon parallel in structure, so the set reads as one family and sorts together.
- **Context and Problem Statement** — the situation and the question,
  including *how it came to be*.
  If a previous design is being replaced,
  say why it was built that way and what changed since
  (usually: the requirements changed) —
  do not present the old design as if it had always been a mistake.
  No options, no evaluation, no decision here.
- **Decision Drivers** — the functional and non-functional requirements
  and the qualities that influence the decision,
  **listed without judgment**.
  This section says what matters and how it will be measured;
  the evaluation belongs in *Pros and Cons of the Options*.
  Write each driver as a named criterion followed by the questions it asks:
  `- **Maintainability:** How much effort is it to maintain and evolve …?
  Does the team have the required expertise? …`
  Make the drivers non-overlapping —
  if a point is already covered by another driver, fold it in rather than
  adding a near-duplicate bullet.
  See *Candidate non-functional requirements* below for a catalog to draw from.
- **Considered Options** — a plain list of the alternatives, titles only.
  If applicable, should include the option of no or small changes,
  e.g., "keep what we have", "keep what we have and fix it incrementally",
  and the meaningful variants of the new proposal.
- **Pros and Cons of the Options** — one subsection **per listed option**,
  none skipped, each with a short description
  followed by `- Good, because …` / `- Neutral, because …` / `- Bad, because …`
  bullets.
  This is where the drivers get evaluated:
  argue each option against the *same* drivers,
  so the sections are comparable.
  State honestly when something is unknown
  (`- Neutral, because it is _unknown_ whether …`)
  instead of turning uncertainty into a pro or a con.
- **Decision Outcome** — `Chosen option: "…", because …`,
  with the justification tied back to the drivers
  (k.o. criterion met, force resolved, best overall).
- **Consequences** — what changes as a result, good and bad,
  including what is lost or breaks for existing users.
- **Risks** — what could go wrong when implementing the decision,
  with a rough magnitude. Repeating points from the cons is fine.
- **Confirmation** — how compliance with the ADR will actually be checked
  (review, test, lint rule, …).
- **More Information** — evidence, follow-up decisions still open,
  revisit triggers, links.

Optional sections may be deleted, but do not delete them just because they are
hard to fill — an empty *Confirmation* or *Risks* is usually a sign the decision
is not finished.

### Candidate non-functional requirements

A catalog to draw drivers from — not a list to work through.
Pick the few qualities that actually decide *this* question and drop the rest;
a driver nobody would trade anything for is noise.

Accessibility, availability, compatibility, data integrity, documentation,
efficiency, extensibility, fault tolerance, flexibility, functional suitability,
interoperability, latency, localization, maintainability, operability,
performance, portability, privacy, readability, reliability, resilience,
reusability, safety, scalability, security, testability, throughput, usability.

Drivers used in this repository beyond that catalog include
the health of an upstream open-source project,
the expertise available in the team,
and packaging and deployment fit (Debian package and container image).

## Supporting the ADR author

The author owns the decision; an agent supplies the evidence and the structure
for it. Offer this work, do not start it unasked — a research sweep is slow,
and the author may already have the answers. Say what it would cover, then let
them pick.

Ground rules:

- Every external claim gets a link.
  Figures get their method written down as well, so a reviewer can re-derive
  them (see `dev/0013-tech-stack-python-http-client.md` for the pattern).
- Record the date of any upstream check.
  Project health goes stale, and that is what `resubmission` is for.
- What you could not verify stays marked as unknown.
  Never promote a guess to a `Good, because …`.
- If your harness has no web access, say so
  instead of answering from training data.
- Do not write the *Decision Outcome*, choose the *approval level*,
  or fill in *coordinated with*.
  Those are the author's calls; draft and ask at most.

Useful offers, by section:

- **Before drafting** — search this repository for records on the same topic
  (`git grep -il <term>` or `grep -ril <term> .`).
  The decision may already exist, or the new ADR may supersede one.
  Report what you found and where it lives.
- **Context and Problem Statement** — reconstruct the history from the linked
  epic or issue, the affected repositories' git history, and earlier ADRs,
  so that "why it was built this way" is sourced rather than recalled.
- **Decision Drivers** — propose a candidate list of functional and
  non-functional requirements, drawn from the linked requirements, from what
  comparable ADRs here used, and from the operator's and the customer's view:
  installation, upgrade, backup, scaling, monitoring, debugging, support,
  and the expertise the team would need.
  Hand it over as named criteria with their questions — unranked and
  unjudged — for the author to keep, cut, or reword.
  Offering the *Candidate non-functional requirements* catalog verbatim,
  as a comment for the author to browse,
  is cheap and often surfaces the quality nobody had thought of yet.
- **Considered Options** — search the problem space for alternatives and prior
  art, including what comparable projects chose and what they say about it
  afterwards.
  Surface the keep-what-we-have variants explicitly;
  a missing option is the most common review finding here.
- **Pros and Cons of the Options** — per option, look up best practices,
  documented limitations, and migration reports from people who have done it.
  Check upstream health: release cadence, date of the last release, number of
  maintainers, open issues, unfixed CVEs, license, and whether it is packaged
  for Debian and as a container image.
  When a claim is measurable — latency, resource use, propagation delay —
  offer a spike or a benchmark instead of an estimate.
- **Consequences** — search the wider estate, not just one repository, for the
  callers and clients of whatever is being changed,
  so that "what breaks" is a list and not an adjective.
- **Risks** — search for known failure modes, CVE history, deprecation notices,
  and the breaking-change record of the proposed solution.
- **Confirmation** — propose a concrete check: a test, a lint rule, a review
  checklist item. Something that can fail.
- **More Information** — collect the links gathered along the way,
  so every claim in the record stays traceable.

Before the merge request, review the draft against *What belongs in each
section*: every considered option has a pros-and-cons subsection, the drivers
carry no judgment and do not overlap, every option is argued against the same
drivers, the metadata block is complete, and `pre-commit run -a` passes.

## Load these skills before writing Markdown

Before writing or editing any Markdown in this repository, load whichever of these
skills your harness offers:

- `remove-claudisms` - strips the words and structural habits that mark text as
  AI-written.
- `semantic-linebreaks` - the line-breaking convention described later in this
  document.
- `style-guide-wordlist` - Univention's per-term rulings, backed by
  `docs/word-list.rst` and `docs/univention-terminology.rst`.
- `univention-style-guide` - Univention's house style for documentation.

Load them **first**, not after a draft exists: they change how the prose is written,
and retrofitting them means rewriting work that was already reviewed.

Where these skills disagree with each other, the Univention ones win:
`style-guide-wordlist` and `univention-style-guide` outrank `remove-claudisms`
on any term they cover.

### When a skill is missing

A missing skill is **not an error**. The skills live outside this repository and not
every machine has them. Do the following:

1. Write the ADR anyway. Never block on a missing skill, and never reconstruct one
   from memory - a half-remembered word list is worse than none.
2. Name the missing skills in your reply, and say which checks you could not run,
   so the author knows what is unverified. "I could not check the draft against the
   Univention word list" is useful; silence is not.
3. Tell the author the missing skills are **recommended**, and **offer to install
   them**. Do not install anything without being asked - it writes outside the
   repository and into the author's home directory.

### Installing the skills

All four come from one repository,
`git@git.knut.univention.de:univention/tooling/ai-workflows.git`.
The documentation skills are under `skills/docs/`; other skills in that repository
sit directly under `skills/`.

Install on request, not on sight:

1. **Look for an existing clone before cloning.** The path differs per machine, so
   search for it instead of guessing a layout:

   ```shell
   find ~/git -type d -name .git -prune -o -type d -name ai-workflows -print
   ```

   Pruning `.git` matters: without it the search also returns
   `.git/modules/…/ai-workflows` for any copy included as a submodule, and that path
   is a bare git directory with no working tree, so a symlink into it is broken.

   Prefer a **standalone clone** over a copy under `vendor/` or a submodule of another
   project. A vendored copy is pinned to whatever revision that project last bumped,
   and it need not carry every skill - on one machine the vendored copy was nine days
   behind and shipped no `remove-claudisms` at all, so linking to it would have
   silently dropped one of the four.

   Clone only if no standalone clone exists, next to the author's other
   repositories:

   ```shell
   git clone git@git.knut.univention.de:univention/tooling/ai-workflows.git \
       ~/git/tooling/ai-workflows
   ```

2. Create both skill directories. Configure **Claude Code and OpenCode together**,
   even when only one harness is in use, so the next session finds the skills
   whichever harness starts:

   ```shell
   mkdir -p ~/.claude/skills ~/.config/opencode/skills
   ```

3. Symlink each skill into both directories, rather than copying, so that a
   `git pull` in the clone updates every harness at once:

   ```shell
   REPO=~/git/tooling/ai-workflows
   for skill in remove-claudisms semantic-linebreaks style-guide-wordlist \
                univention-style-guide; do
       ln -sfn "$REPO/skills/docs/$skill" ~/.claude/skills/"$skill"
       ln -sfn "$REPO/skills/docs/$skill" ~/.config/opencode/skills/"$skill"
   done
   ```

4. Load the newly installed skills in the running session and apply them to the
   draft. Most harnesses pick up new skills without a restart; if yours does not,
   say so and ask the author to restart it.

Report what you installed and where the symlinks point, so the author can undo it
with `rm` on the links alone.

## Spelling: American English, not British English

Write American English everywhere:
prose, documentation, comments, identifiers, commit messages and chat.

- `behavior`, not `behaviour`; `color`, not `colour`; `license`, not `licence`.
- `-ize` / `-ization`, not `-ise` / `-isation`: `initialize`, `serialization`.
- `-log`, not `-logue`: `catalog`, `dialog`.
- Keep the British form when it is already fixed by the surrounding text,
  an existing identifier, or a third-party API: `HttpResponse.colour_scheme`
  stays as spelled.

Older records in this repository predate the rule and are not to be rewritten for it;
apply it to the lines you are editing, as with Semantic Line Breaks.

## Prose style: Semantic Line Breaks

Not required, but expected as good practice, and it keeps MR diffs small,
which makes ADRs much easier to review comment-by-comment.

- Break after every sentence (`.`, `!`, `?`),
  and after clause boundaries (`,`, `;`, `:`, `—`) where it aids readability.
- Never break inside a hyphenated word, a link, or a code span.
- Target 80 columns; the `line-length` lint rule is disabled,
  so this is a guideline, not an error.
- The rendered output must stay identical to continuous prose.
- **Reflow only the lines you are already editing**, never the surrounding prose —
  a reflow-everything commit destroys the reviewability it is meant to protect.
- Leave code blocks, tables, and the metadata block untouched.

Apply this **only** to `.md` files in the repository.

## Editing an ADR in review

- Reviewers work with GitLab suggestion blocks on individual lines.
  When applying review feedback, change exactly what the thread asks for;
  do not opportunistically rewrite adjacent paragraphs,
  or the remaining suggestions stop applying cleanly.
- Never change an `accepted` record's decision in place.
  Write a new ADR that supersedes it.
