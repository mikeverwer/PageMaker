<!-- ---
meta-description: An interactive Tableau dashboard exploring twelve years of publicly reported cyber events, built on the University of Maryland's Cyber Events Database.
meta-robots: index, nofollow
meta-viewport: width=device-width, initial-scale=1.0
title: The Cyber Threat Landscape
---
{ } -->


[View the interactive dashboard on Tableau Public](https://public.tableau.com/app/profile/mike.verwer/viz/CyberEvents_17842459556440/CyberThreatLandscape2014-2025)

## The Dataset

The underlying data is the [Cyber Events Database](https://cissm.umd.edu/cyber-events-database), maintained by the Center for International and Security Studies at Maryland (CISSM) and the Center for Governance of Technology and Systems (GoTech) at the University of Maryland. The database compiles publicly reported cyber incidents from 2014 onward, collected by scraping known open-web and dark-web sources and, beginning in 2025, by keyword searches against the GDELT Project's global news monitoring datasets. Candidate events are deduplicated and manually reviewed by researchers, who classify each incident's threat actor type, motive, target industry, and effects according to a published taxonomy. The snapshot used here was downloaded in April 2026 and contains 16,532 events spanning 2014 through February 2026.

Two properties of the data are worth stating up front, because they shape what the dashboard can and cannot claim. First, the database records publicly *reported* incidents, so it inherits the biases of public disclosure: events are only recorded once disclosed, and the gap between an event's date and its reporting date is often measured in years. Second, attribution is sparse and secondhand. Only about 24% of events carry an attributed actor country, and the codebook is explicit that attributions are taken directly from source material without independent validation. Every geographic claim about attackers below should be read with that caveat attached.

The raw CSV also needed preprocessing before it was usable in Tableau. I wrote a short Python script to standardize inconsistent category values before loading the data. The script itself, what it changes, and how to reproduce the cleaned dataset are covered at the end of this page.

## Dashboard Design

The dashboard is organized around a single color scheme keyed to the database's three event types: *disruptive* events (pink) impede a target's normal operations, *exploitative* events (teal) illicitly access or exfiltrate sensitive information, and *mixed* events (orange) do both, with double-extortion ransomware as the canonical example.

The user starts from a high-level overview of all events and narrows in through interaction. Clicking a year in the temporal chart, an actor type in the crosstab, or a country on the map filters every other chart in unison, and a parameter control toggles the map between two views: where targets are located and where attackers operate from.

The published workbook also has a second tab, **Top Actors**, which ranks the most active named threat actors as a bar chart colored by actor type, with a parameter slider controlling how many are shown. It makes for a quick read on who is actually behind the volume: ransomware crews like cl0p and LockBit sit alongside hacktivist collectives like NoName057(16) and Anonymous, with state-linked units further down the list.

A few design decisions are worth explaining.

**A logarithmic color scale on the map.**
: The geographic distribution of targets is extremely skewed: the United States alone accounts for 47% of all targeted events in the dataset. On a linear color scale, nearly every other country would render as visually indistinguishable from zero. Coloring by the logarithm of the event count compresses that range, so a country with 50 events remains distinguishable from one with 500 while the United States retains its visual dominance. The two map views use distinct sequential palettes (blue for targets, red for actors) so the toggle is legible at a glance.

**Decomposing multi-valued motives.** 
: Many events carry more than one motive tag, such as an attack that is both financially motivated and an act of sabotage. Rather than treating each combination as its own category, I decomposed the field into per-motive indicator flags, so an event tagged with two motives is counted under both. Motive totals can therefore exceed the total event count, but the alternative, a proliferation of compound categories, would fragment the picture and understate every individual motive.

**Scoped filter actions.** 
: Each cross-filtering action is scoped deliberately rather than left at Tableau's defaults. Source sheets are excluded from their own filter actions, and the country-selection action excludes the charts where country-level filtering would be misleading. Without this scoping, clicking a mark filters the very chart it came from, collapsing it to a single bar and stranding the user.

**What gets filtered out.** 
: Three major filters are applied at the source level. Events from 2026 are excluded because the snapshot covers only January and February of that year and, on a chart with full-year steps, a partial year reads as a steep decline that is not real. Events with an undetermined actor type are excluded (786 rows, about 5%) because the actor type crosstab is the dashboard's primary interactive filter, and an unknown bucket there degraded the experience. Before dropping them I checked whether they were concentrated in ways that would distort the story. Undetermined attribution clusters in the earliest and most recent years, which tracks with how attribution works in practice: recent events have not been investigated yet and older ones predate better classification. The years driving the dashboard's main trend, 2022 and 2023, have almost no undetermined actors, so the shape of that trend holds either way. Finally, events with an undetermined event type are excluded (211 rows, about 1%) because the event type color is the visual backbone of every chart, and unclassified records would add a fourth color with no meaning. After overlaps, the three filters remove 1,125 of the 16,532 events, leaving the 15,407 shown in the dashboard's grand total.

**Two maps stacked in one zone.** 
: The target and actor maps are separate sheets occupying the same space on the dashboard. Simply layering them does not work, because the sheet on top intercepts mouse events even when the toggle has emptied it, leaving the visible map unclickable. Instead, each map sits in its own container whose visibility is controlled by a boolean field driven by the toggle parameter, so the hidden map is removed from the interaction layer entirely and whichever map is shown stays fully interactive.

## What the Data Shows

Event counts grow dramatically across the decade, from 633 recorded events in 2014 to a peak of 2,566 in 2022. Exploitative events dominate throughout, but the mixed category grows markedly from around 2019, which aligns with the documented rise of double-extortion ransomware: attackers no longer choose between encrypting systems and stealing data, and the dataset registers that shift directly. Counts fall off after 2023, but this is at least partly an artifact of reporting lag rather than a genuine decline, since recent events have had less time to surface publicly. The dataset's paired event and reporting dates make that lag directly visible.

Filtering the temporal chart to nation-state actors shows disruptive activity peaking in 2022, coinciding with Russia's invasion of Ukraine and the surge of state-linked cyber operations surrounding it.

Motive tells a similarly conditional story. Financial gain dominates overall, and filtering to criminal actors produces an almost entirely financial landscape, as expected. Filtering to nation-states inverts the picture: political espionage leads, followed by sabotage, with financial motives still present. That residual financial activity among state actors is not noise; it reflects groups like North Korea's Lazarus Group, which runs financially motivated heists to fund state operations.

Geographically, the United States is by far the most targeted country. On the actor side, Russia leads attributed origins by nearly an order of magnitude over China and North Korea, though the attribution caveat above applies with full force here, since these figures describe only the minority of events where sources named an origin.

Among industries, Public Administration is the most targeted sector overall, followed by Health Care and Social Assistance and then Information. Filtering to criminal actors moves Health Care to the top, which is consistent with the sector's combination of highly sensitive personal data, aging IT infrastructure, and constrained security budgets. The prevalence of mixed-type events in healthcare is the most concerning pattern in the dashboard, since ransomware that takes hospital systems offline carries risks beyond data loss.

## Limitations

The dashboard describes reported events, not all events, and the reporting process is neither immediate nor uniform across countries and sectors. Attribution figures rest on source claims rather than independent verification and cover roughly a quarter of the dataset. These limits do not undermine the broad patterns, which are robust across filters, but they do mean the dashboard is a map of the publicly visible threat landscape rather than the landscape itself.

## Preprocessing 

The CISSM CSV snapshot goes through a pandas cleaning script, the cleaned file is loaded into Tableau as an extract with the data source filters described above applied, and the finished workbook is published to Tableau Public.

The cleaning script exists because the raw snapshot contained several variants of the same category differing only in casing, spacing, or pluralization. `Exploitation Of Application Server`, `Exploitation of Application Servers`, and `Exploitation of application server` all describe one event subtype, but Tableau treats each text variant as its own category. Without the fixes, the map splits a single country across two marks and the subtype filters show duplicate entries for what is really one thing.

```python
import pandas as pd

INPUT_FILE = "cyber_events_2026-04-05.csv"
OUTPUT_FILE = "cyber_events_cleaned.xlsx"

df = pd.read_csv(INPUT_FILE, low_memory=False)

# Fix known typos and inconsistencies
subtype_fixes = {
    'Exploitation Of Application Server': 'Exploitation of Application Server',
    'Exploitation of Application Servers': 'Exploitation of Application Server',
    'External Denial Of Service': 'External Denial of Service',
    'External denial of service': 'External Denial of Service',
    'Exploitation Of Network Infrastructure': 'Exploitation of Network Infrastructure',
    'Exploitation of  Network Infrastructure': 'Exploitation of Network Infrastructure',  # double space
    'Exploitation of Network Server': 'Exploitation of Network Infrastructure',
    'Exploitation of application server': 'Exploitation of Application Server',
    'Data Attack;Exploitation of Application Server': 'Data Attack,Exploitation of Application Server',
}
country_fixes = {
    'United States of America' : 'United States Of America',
    'United Kingdom of Great Britain and Northern Ireland': 'United Kingdom Of Great Britain And Northern Ireland'
}
actor_country_fixes = {
    'United States of America': 'United States Of America',
    'United Kingdom of Great Britain and Northern Ireland': 'United Kingdom Of Great Britain And Northern Ireland',
    'Iran (the Islamic Republic of)': 'Iran (Islamic Republic of)'
}
motive_fixes = {
    'Political-espionage': 'Political-Espionage'
}

columns_to_fix = {
    'event_subtype': subtype_fixes,
    'country': country_fixes,
    'actor_country': actor_country_fixes,
    'motive': motive_fixes
}

for col, fixes in columns_to_fix.items():
    df[col] = df[col].astype(str).str.strip('[]')
    for old, new in fixes.items():
        df[col] = df[col].str.replace(old, new, regex=False)

df.to_excel(OUTPUT_FILE, index=False)
```

In total, the script collapses nine typo and casing variants in `event_subtype` (111 rows affected), normalizes the casing of the long-form United States and United Kingdom names in `country` and `actor_country` (about 8,900 rows, the large majority of them the US), and fixes one casing variant in `motive` (26 rows). It also strips stray square brackets from those fields along the way.

The dataset itself is not something I can hand out. CISSM makes descriptive information about the database public but asks that anyone who wants the full records contact the project maintainers directly, so what's here is the cleaning process rather than the data. To reproduce the cleaned dataset, request the data through the [Cyber Events Database](https://cissm.umd.edu/cyber-events-database) page, point `INPUT_FILE` at your download, and run the script with pandas and openpyxl installed. Connecting Tableau to the resulting `cyber_events_cleaned.xlsx` rebuilds the workbook's data source.

If you use the data in published work, CISSM asks that you cite:  
> Harry, C., & Gallagher, N. (2018). Classifying Cyber Events. *Journal of Information Warfare*, 17(3), 17-31.

[View the dashboard on Tableau Public](https://public.tableau.com/app/profile/mike.verwer/viz/CyberEvents_17842459556440/CyberThreatLandscape2014-2025) · [Dataset and codebook](https://cissm.umd.edu/cyber-events-database)
