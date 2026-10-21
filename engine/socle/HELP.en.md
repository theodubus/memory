# The socle, on the human's side: user guide

This guide describes how to use a project equipped with the socle, from the
point of view of the human who leads it: their role, each action with its
command, what to do when a check refuses, and the reference of the
commands, the policy and the thresholds. It assumes the socle is
installed; what the socle is, its principle and its installation are
presented in the README of its repository.

Commands run at the project root: `python3 .socle/socle <command>`. This
guide is shown by `python3 .socle/socle help`.

## The human's role

The agent writes the code, the tests, the documentation and the memory;
the checks verify its work. The human steps in on four points:

- **answering the agent's requests**, when a decision belongs to them;
- **approving their own changes** to protected files;
- **performing the actions only the human can perform**: those the hook
  refuses to the agent (pushing to the default branch, publishing, remote
  deletion, spending) and service settings (GitHub, private repository).
  The agent records them in the backlog with `for : human` and how to do
  them; the state lists them;
- **setting the autonomy policy**, `.socle/policy.toml`, which only they
  modify.

### The autonomy policy

The policy has eight rules, which the agent applies and the hooks enforce:

1. Loosening a guardrail (`.socle/guardrails.toml`) requires an approved
   request; tightening is free.
2. Deleting a test or changing an expected value requires an approved
   request, or a specification the human changed themselves that names the
   test.
3. A reversible and measurable design decision, the agent takes and
   records; a decision that is costly to undo, it asks for.
4. An irreversible or external action is always asked for; the hook
   refuses it to the agent.
5. The memory is append-only; a "refuted" fact cites the measurement that
   refutes it; "validated" is only written after the human's answer.
6. A defect next to the current work goes to the backlog; it is only fixed
   if it blocks.
7. After three failures of the checks in a row, the agent stops and writes
   a request that sums up what it tried.
8. An expected approval is never guessed: the agent queues the request and
   works on something else.

## Following the project

- `python3 .socle/socle state` prints the project's state, computed on each
  call: the commit, the CI and whether GitHub requires it before merging,
  the backlog, the pending requests, what is up to the human, then the
  active work and the facts. The agent receives the same state at the start
  of each session.
- Each intervention of the agent that acted ends with two lines: "For
  you:", what is up to the human, and "Next:", what comes next.
- The memory is read in `memory/`: the facts and their proofs, the active
  work, the decisions, the journal, the backlog, the requests. Its format
  is specified in `.socle/engine/socle/FORMAT.md`.

## Actions

### Describing the project

Right after the installation:

```sh
python3 .socle/socle init --brief <document> --repo
```

The brief is archived as is; `--repo` surveys what the repository already
holds (tools, tests, CI). Without a document, `--repo` alone; in an empty
repository, no option. The agent then asks, in the conversation, a few
starting questions, each with its default.

### Answering a request

When a decision belongs to the human, the agent writes a request, pushes
it and gives its link. The request reads on its own: the decision, the
context, the options, the recommendation, and the list of possible
answers, at its end.

Answer in the conversation with one of those answers, with a precision if
needed; the agent records the answer with the human's exact text.
`approve` is the only answer that authorises an action reserved to the
human (loosening a threshold, deleting a test, changing a protected file).
`insufficient-context` sends the request back to the agent, which rewrites
it.

Outside the conversation, from a terminal:

```sh
python3 .socle/socle answer D-NNNN <answer> --text "<text of the answer>"
```

An answered request is frozen: it no longer changes.

### Recording a decision taken in session

A question settled on the spot, with the human present (approving a spec,
settling an open question), needs no full request: answer in the
conversation; the agent immediately records the question and the answer,
word for word, in the same register as the requests (`socle decision`).

### Approving one's own protected changes

The policy, the thresholds, the adapter, the hooks, the CI and the engine
are protected: a commit that changes them without approval is refused.
When the change comes from the human (a socle update, a modified policy):

```sh
python3 .socle/socle approve --text "<reason>"
```

The command lists the changed protected files, then approves them on
confirmation by writing an approved request, to commit with them. It is
reserved to the human: the hook refuses it to the agent, which then cites
the number of that approval.

### Reviewing before publication

If the policy requires it (`review` in the `[private]` section), nothing
goes to the public repository without the human's agreement: the agent
shows what goes out, the human answers in the conversation, and the agent
records the agreement. From a terminal:
`python3 .socle/socle reviewed --by <name>`.

### Committing oneself

The human's commits go through the same checks. A public function added or
changed is named by a test, or waived in the commit message
(`Waive-test: f — <reason>`); the hook points it out at commit time, and
the CI refuses without it. A fix (subject `fix:`, or trailer
`Fixes: B-NNNN`) brings a test that fails on the parent commit.

### Setting up the private memory in companion mode

In companion mode, the private memory lives in a second, private
repository. Create that repository, empty, on GitHub, then:

```sh
python3 .socle/socle private install --repo <address of the private repository>
```

The command clones the private repository, makes its first commit, writes
the lock and creates a deploy key. It ends with the two actions left on
GitHub (the deploy key of the private repository, two secrets of the
public repository), with the link of each page. It is reserved to the
human.

### Protecting the default branch

After the first push, on GitHub, in the repository settings ("Rules"):
create a ruleset that requires, before any merge, the socle's CI ("Socle —
verify, checks, self-test") and the code owners' review. Without it, a
red CI does not prevent merging. `socle state` says whether the CI is
required.

### Removing a duplicate start-of-session state

If the project already had its own `SessionStart` hook, the installer
points it out: each session would receive two overlapping states. Remove
that hook from `.claude/settings.json`, or keep in it only what is the
project's own. It is an agent setting, modified by the human only.

### Updating the socle

Run the installation command again from an up-to-date copy of the engine.
The engine is replaced as a whole; the project's files are never
overwritten, and the diff of the policy is shown without modifying it. The
protected files changed by the update are then approved
(`socle approve`), and committed.

## With BMAD Method

When BMAD Method is installed in the project, it plans (brief, PRD,
architecture, epics, stories, specs, sprint) and the socle proves and
retains. Everyday use:

- **Run a BMAD workflow** as usual, by naming it to the agent (for
  instance the build workflow, `bmad-build`). The socle's installer has
  set the customisation of each BMAD skill: on activation, the agent reads
  the socle's state; at the end of the workflow, it keeps the memory up to
  date and finishes with green checks.
- **Approving a spec.** When the workflow stops to have a spec approved,
  answer in the conversation. The agent records the approval word for
  word, as a decision taken in session that cites the spec, before writing
  the code. A spec that requires this approval does not leave the draft
  state without it, and its frozen intent no longer changes without a new
  approval: the `bmad.approbation` check verifies it.
- **Deferred work.** What BMAD defers (its list of deferred work) enters
  the socle's backlog through `python3 .socle/socle bmad-import`, which
  the agent runs; the `bmad.reports` check refuses deferred work left out
  of the backlog. The backlog remains the single list of findings.
- **What the state shows in addition**: the unfinished specs, the stories
  in progress or in review, the open retrospective actions, and the BMAD
  skills without the socle's customisation.
- **BMAD's files** (its skills, its scripts) are declared third-party in
  `.socle/guardrails.toml` (`[thirdparty] paths`) and escape the checks.
  Its planning documents are checked like the rest. Declaring other
  third-party files is a loosening: it requires an approved request.
- **Updating BMAD** is BMAD's business
  (`npx bmad-method install --action update`); running the socle's
  installation again then sets its customisation on the new skills.

## When a check refuses

Each refusal says what it saw and how to get out of it. The most common:

| What refuses | Meaning | What to do |
| --- | --- | --- |
| `protege.fichiers`, at commit time | a protected file changed without approval | if the change comes from the human: `socle approve --text "<reason>"`; if it comes from the agent: a request |
| `cliquet.garde-fous` | a threshold was loosened | restore it, or an approved request that cites the key |
| `tests.attendus` | an expected value changed, or a test disappeared | an approved request that names the test, or a specification changed by the human |
| `tests.code-teste`, in CI | a public function without a test that names it | write the test, or `Waive-test: f — <reason>` in the commit message |
| `tests.regression`, in CI | a fix without a test that fails on the previous commit | write that test |
| `docs.correspondance` | code tied to a document changed without it | update the document, or `Waive-doc: <reason>` in the commit that changes that code |
| `memoire.lectures` | a cited fingerprint no longer matches | read the entry or the index again (`socle show`), cite the fingerprint shown |
| `memoire.collisions` | an identifier taken by the branch was also taken on the default branch | `socle renumber <ID>`, which assigns the next free one and carries the citations over |
| `memoire.retard`, at the end of a turn | code changed and the memory did not | update the active work, the journal or the backlog |
| end of turn refused, "For you:" | the agent's last message lacks its recap | end with the recap and the two lines |
| `prive.verrou` | the companion repository's lock is missing or behind | `socle private lock`; with no repository in place, `socle private install --repo <address>`, by the human |
| `mutation.couverture` | a module that holds code has no cap | add it "to be measured", then `socle mutation-run --record`, or take the cap from the last scheduled sweep |
| `mutation.vivante`, in CI | the scheduled sweep is suspended, or has not run for fifteen days | re-enable it in GitHub's Actions tab and run it by hand; it is a human action |
| `bmad.reports` | work deferred by BMAD is not in the backlog | `socle bmad-import` |
| push refused, review | the policy requires the human's review | the human reviews what goes out; the agent records their agreement |

A hook can be bypassed locally (`--no-verify`); the CI runs everything,
and the agent is not allowed to bypass a hook. The CI stops nothing by
itself: a red CI only prevents merging if the default branch requires it
(see "Protecting the default branch").

## Reference

### Commands

| Command | Use |
| --- | --- |
| **For the human** | |
| `help` | this guide |
| `install` | install or update the socle |
| `init` | initialise the memory from a brief, the existing repository, or nothing |
| `state` | the project's state, computed on each call |
| `answer` | answer a request |
| `decision` | record a decision taken in session |
| `approve` | approve one's own protected changes (human only) |
| `reviewed` | record the review before publication |
| `private install` | set up the companion repository (human only) |
| **For the agent** | |
| `new`, `next-id` | add an entry to the memory, with its computed identifier |
| `show`, `url` | show an entry with its fingerprint; give the link of a file |
| `verify`, `check`, `checks` | run the language's tools and the checks; list the checks |
| `private` | private memory status, lock, terms, moving an entry |
| `mutation-run`, `mutation-verdict` | run the mutation sweep and judge its survivors |
| `renumber`, `archive` | renumber a colliding entry; file the closed topics |
| `bmad-import` | bring the work deferred by BMAD into the backlog |
| **Internal** | |
| `hook`, `ci`, `selftest`, `fingerprint` | the hooks, the CI, the self-test, the engine's fingerprint |

`python3 .socle/socle <command> --help` details the options of each.

### Thresholds and the ratchet

`.socle/guardrails.toml` holds the checks' thresholds: the size budgets of
each memory layer, the mutation caps per module, the correspondences
between code and documentation, the values tied to their source, the
minimum size of a copy, the specification paths, the third-party files.
The ratchet compares each key with the base's, with a direction per key (a
lower budget is stricter, a shorter list of exclusions too). Tightening is
free; loosening fails the CI as long as no approved request cites the key.
An unknown key that changes counts as a loosening.

Protected files (the policy, the adapter, the engine's lock, the hooks, the
CI, the human's answers) only change with an approval that cites their
path and their new fingerprint.

### Checks

`python3 .socle/socle checks` lists each check, the stages where it runs
and what it verifies.
