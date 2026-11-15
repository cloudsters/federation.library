# federation.library

**Checked releases for every commons.**

A commons is shared value creation: a life, an organisation, a community, a city or an ecosystem. Its CORE is a cybernetic model of that value creation, kept as plain files that people and agents work on together. This library holds what such a CORE installs: the Commons model with the discipline's specifications and tools, the patterns of Commons Engineering, and the models of the domains in which value is created.

Every release here has passed its gate, carries a record with its digest, and never changes once released. A commons decides which releases it installs and when it adopts a newer one.

## What the library holds

| Release | What it is | Where it goes in a CORE |
| --- | --- | --- |
| `commons` | The Commons model: the specifications of the discipline and the tools that check and serve a CORE | `models/commons/commons-engineering/commons/` |
| `patterns` | The patterns extract: the patterns of Commons Engineering from the most general orbit inward, each with its relations and contributors | `patterns/commons/commons-engineering/` |
| `life` | The domain model of a life and its value creation | `models/commons/commons-engineering/life/` |
| `health` | The domain model of health and care | `models/commons/commons-engineering/health/` |
| `business` | The domain model of a business, in its variants `business/startup` and `business/corporate` | `models/commons/commons-engineering/business/<variant>/` |
| `urban` | The domain model of a city and its quarters | `models/commons/commons-engineering/urban/` |

Each domain model releases its public part here. Its depth stays in the knowledge of its CORE and is served only through `federation.mcp`, to members from OPEN inward.

`index.yml` lists every release, earlier ones included, with the path and digest of its record and its state: `candidate`, `released` or `retired`. An earlier release stays installable for the commons that pin it. `library.yml` names the library and any release it withholds.

## Install a release

Install the Commons model first; its tools then install everything else. From the root of your CORE:

```sh
python models/commons/commons-engineering/commons/specs/tools/install.py . \
  --from <release folder or zip> \
  --expect sha256:<the record digest from index.yml>
```

The copy is checked against the digest the index gives before anything is written. Only a release that passes is moved into place, recorded in `.commons/lock.yml` with its origin and digest, and pinned in `.commons/commons.yml`. On any failure nothing changes. Installed copies stay whole and read-only; what your commons adapts becomes its own record and keeps its origin.

A patterns extract installs the same way, checked against its record. Where your CORE keeps a graph, the extract becomes one of its sources. A CORE holds one extract per library.

## Take up a newer release

A newer release never overwrites the one you hold. Your commons takes it up by decision, on a working branch:

```sh
python models/commons/commons-engineering/commons/specs/tools/install.py . \
  --from <newer release> --expect sha256:<its digest> --take-up
```

The new copy is checked as at install and takes the place of the older one, which git keeps in your history. The lock and the pin then name the newer version. Records your commons built from the older release are taken up one by one with `take_update.py`, so nothing of your own changes without your decision.

## Versions and retirement

A version is released once and is never changed or deleted. It ends when a later release names it in its `retires`, with a date; from then on the index shows it as `retired`, and it stays installable for every commons that pins it.

A release that turns out to carry private data, an unauthorised part or a licence the library may not give is withheld: `library.yml` names it, the library stops distributing its files, and its record stays. Each commons that holds a copy finds it through its own where-used and decides what follows.

## Read the library

Every release here can be read directly from this repository, without an account. The depth of the domain models is served to members through `federation.mcp`, after signing in; the generated `AGENT.md` of a CORE names the connection.

## How content arrives

Content arrives by pull request only. A release comes from the release event of its source and passes the library's gate before it is merged: its files must match the digest of its record, its record must be well formed, and it must carry no private datum and no licence the library may not give. The index is generated from the records and never kept by hand.

## Licence

The domain models (`life`, `health`, `business`, `urban`) and the patterns extracts are released under **CC BY-SA 4.0**. Each release names its licence in its record. Attribution to the patterns' sources and contributors travels with each pattern and must be kept in every adaptation.

This library is held for Commons Engineering and stewarded by the **cloudsters FEDERATION** ([cloudsters.net](https://cloudsters.net)).
