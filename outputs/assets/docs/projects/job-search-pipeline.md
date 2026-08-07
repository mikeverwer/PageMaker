# A Fully Local Job-Search Pipeline

Searching for work involves a great deal of repetitive reading. Each morning brings a new batch of postings, most of which can be dismissed within seconds, and a small number that deserve careful attention. The scanning portion of this routine is mechanical, which makes it a natural candidate for automation. This project is a pipeline that runs once per day: it fetches recent postings from a job-search API, scores each one against my profile, and delivers a ranked digest to my inbox. It has become a supplemental channel in my own search, providing a consistent daily read on the market while my focused attention goes to the postings that merit it.

The system's defining constraint is that it runs entirely on local infrastructure. Orchestration is handled by n8n, self-hosted in Docker, and all language-model inference is performed by Qwen 2.5 7B Instruct, an open-weight model served locally through Ollama. The only outbound network traffic is the call to the job API and the outgoing email; no per-token fees are incurred, and no data leaves the machine. The more interesting consequence of this constraint is that the model doing the judging is small, and the limitations of a small model shaped the architecture in ways I think are worth describing.

## What the pipeline does

![Pipeline architecture](/assets/images/job_search_pipeline_architecture.png)

Every run begins by loading a single configuration file that describes the entire search: the candidate profile, target roles, skill lists, location tiers, seniority markers, scoring weights, and model parameters. All downstream stages read from this one source, so tuning the system requires a change in one place rather than edits scattered across the pipeline.

The pipeline then fetches the day's postings from the JSearch API, sanitizes the description text, and truncates it to a manageable length. Postings already seen on a previous run are filtered out against a persistent store of job identifiers, which is pruned on a thirty-day cycle so it cannot grow unboundedly. Each remaining posting is sent individually to the local model along with a scoring rubric. The model's reply is constrained to a strict JSON schema at generation time[^1], so every response arrives as a well-formed score object. Once all postings are scored and ranked, a second model call produces a short prose summary of the day's market; it is explicitly instructed not to restate individual postings, since the ranked table beneath it in the email handles that deterministically. The summary, the table, and a footer printing the active scoring weights are assembled into an HTML email, which means every digest documents the logic that produced it.

![The workflow in the n8n editor](/assets/images/n8n_canvas.png)

[^1]: The schema is enforced during generation via Ollama's `format` parameter rather than validated after the fact.

## Dividing the labour

The most instructive design problem was deciding what the model should be trusted to do. Early versions delegated every judgment to it: skill assessment, seniority classification, and location fit. Two of the three failed reliably. Location scores collapsed to zero on nearly every posting, and seniority assessments contradicted themselves, sometimes flagging a role as disqualifying in one field of the response while describing it as a good fit in another.

The diagnosis is that these are lookup problems. Determining whether a city lies within my target corridor amounts to checking it against a list; determining whether a role is senior is, in the great majority of cases, a matter of reading the title. Asking a seven-billion-parameter model to reason its way to these answers converts a trivial computation into an unreliable inference. The revised design computes both values deterministically from the configuration before any model call is made and passes them into the prompt as given facts. Should the model produce its own location score anyway, the deterministic value overwrites it.

What remains for the model is the work it is genuinely suited to: reading a long, inconsistently formatted job description and judging how its stated requirements align with my demonstrated skills, then writing a concrete justification grounded in the posting's specifics. This is a comprehension task, and even a small local model performs it well once it is no longer being asked to double as a gazetteer.

## Scoring and gating

Each posting is scored on five dimensions, combined as a weighted average:

| Dimension | Weight | What it measures |
|---|---|---|
| Skill match | 35% | Overlap between the posting's required tools and my demonstrated skills |
| Seniority fit | 30% | Whether the role is reachable for a junior career-switcher |
| Location fit | 15% | Pre-computed tier score, never derived by the model |
| Growth signal | 15% | Whether the role builds toward my identified skill gaps |
| Compensation fit | 5% | Salary alignment where listed; neutral when absent |

The weights reflect the priorities of the search: what a role requires day to day, and whether it is reachable, matter considerably more than geography or listed salary in my case. The growth dimension is worth a note. It rewards postings that would develop the skills I have identified as gaps, currently dbt, Airflow, and cloud warehousing, so the ranking accounts for the direction of the search as well as its present state.

Disqualification is handled separately from scoring. A junior candidate is simply unqualified for a role titled Senior or Principal, and blending that role's poor seniority score into a weighted average would produce a middling number that conceals the actual reason it fails. Roles that trip the seniority gate instead have that dimension forced to a floor value and their final score capped, however well the remaining dimensions scored. The model's own holistic score is preserved alongside the computed one; a posting that scores well with the model yet fails the gate describes a role that suits the general profile, and these cases carry information the pipeline should not discard.

## Status and further work

The pipeline is active and runs each morning on a schedule. Two extensions are planned. The configuration already reserves an embedding model for a retrieval stage, which would allow postings to be compared against the profile in vector space before any generative call is made. The second builds on the gated postings described above: roles that score well but fail the seniority gate form a natural labelled set, and accumulating them over time would provide a basis for evaluating and tuning the scoring rubric against observed market data.

The complete implementation, including the workflow export, all node code, and a technical README covering setup and configuration, is available in the [public repository](https://github.com/mikeverwer/JobSearchPipeline).
