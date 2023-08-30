
# {short title of solved problem and solution}

---

- status: {draft | submitted to TDA | accepted | rejected}
- supersedes: { - | [ADR-0004](0004-example.md)}
- superseded by: { - | [ADR-0005](0005-example.md)}
- date: {YYYY-MM-DD when the decision was last updated}
- author: {contact or informed captain for this ADR}
- approval level: {low | medium | high} <!-- (see explanation below) -->
- coordinated with: {list everyone involved in the decision and whose opinions were sought (e.g. subject-matter experts)}
- source: {(link to) ticket / epic / issue that lead to the creation of this ADR}
- scope: { - | ADR is only valid {until date | until event | as a workaround until better solution … exists}
             | in project … | in product … (defaults to the directory this ADR is stored in)}
- resubmission: { - | YYYY-MM-DD if the scope is time-limited}

<!--
Explanation "approval level"

- low: Low impact on platform and business. Decisions at this level can be made within the TDA with the involved team(s). Other stakeholders are then informed.
- medium: Decisions of medium scope, i.e. minor adjustments to the platform or strategic decisions regarding specifications. The approval of the product owner is requested and the decision is made jointly.
- high: Decisions with a high impact on the business and IT. Changes that have a high-cost implication or strategic impact, among other things. These types of decisions require the decision to be made together with the leadership board.
-->

---

## Context and Problem Statement

{Describe the context and problem statement, e.g., in free form using two to three sentences or in the form of an illustrative story.
 You may want to articulate the problem in form of a question and add links to collaboration boards or issue management systems.}

## Decision Drivers

<!-- This is an optional element. Feel free to remove. -->

<!-- Include qualities and architectural principles that influence the decision,
     e.g. simplicity, standardization, modularity, security, robustness, scalability, …
     See also https://git.knut.univention.de/groups/univention/dev-issues/-/wikis/home
-->

- {decision driver 1, e.g., a force, facing concern, …}
- {decision driver 2, e.g., a force, facing concern, …}
- … <!-- numbers of drivers can vary -->

## Considered Options

- {title of option 1}
- {title of option 2}
- {title of option 3}
- … <!-- numbers of options can vary -->

## Pros and Cons of the Options

<!-- This is an optional element. Feel free to remove. -->

### {title of option 1}

<!-- This is an optional element. Feel free to remove. -->

{example | description | pointer to more information | …}

- Good, because {argument a}
- Good, because {argument b}
- Neutral, because {argument c}  <!-- use "neutral" if the given argument weights neither for good nor bad -->
- Bad, because {argument d}
- … <!-- numbers of pros and cons can vary -->

### {title of other option}

{example | description | pointer to more information | …}

- Good, because {argument a}
- Good, because {argument b}
- Neutral, because {argument c}
- Bad, because {argument d}
- …

## Decision Outcome

Chosen option: "{title of option 1}", because
{justification. e.g., only option, which meets k.o. criterion decision driver | which resolves force {force} | … | comes out best (see below)}.

### Consequences

<!-- This is an optional element. Feel free to remove. -->

- Good, because {positive consequence, e.g., improvement of one or more desired qualities, …}
- Bad, because {negative consequence, e.g., compromising one or more desired qualities, …}
- … <!-- numbers of consequences can vary -->

### Risks

<!-- It's OK to repeat points from the above "Cons of the Options". -->
<!-- Maybe use "Risk storming" to identify risks. -->

- When implementing the decision, a {small, medium, high} risk exists, that {…}.
- …

### Confirmation

{Describe how the implementation of/compliance with the ADR is confirmed. E.g., by a review or an ArchUnit test.
 Although we classify this element as optional, it is included in most ADRs.}

## More Information

<!-- This is an optional element. Feel free to remove. -->

{You might want to provide additional evidence/confidence for the decision outcome here and/or
 document the team agreement on the decision and/or define when this decision and how the decision
 should be realized and if/when it should be re-visited and/or how the decision is validated.
 Links to other decisions and resources might appear here as well.}
