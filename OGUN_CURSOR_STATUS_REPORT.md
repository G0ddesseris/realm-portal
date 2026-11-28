# Ogun Cursor Status Report — Veblen Portal

**From:** Node 5 / Ogun (Cursor IDE)  
**To:** Local Mother Base (Orbit Command)  
**Workspace:** `D:\RealmOfChaos\Veblen_Portal`  
**Airlock:** `D:\MotherBase\06_Swarm_Airlock\Ogun`  
**Date:** 2026-10-25  
**Classification:** Internal ops. No storage passwords, patron emails, or private invite URLs.

**Operator:** Goddess / GitHub `G0ddesseris`  
**Role on this node:** site construction, GitHub Pages deploy, Bunny.net CDN video.

---

## 0. Verdict

The portal is **live and serving**. Custom domain, hero loop, Core feed, and Elite feed are on `main`. Core and Elite are **newest-first feeds**, not a series that starts at `001`.

| Check | State |
| --- | --- |
| Live site | https://therealmsofchaos.com/ |
| Pages fallback | https://g0ddesseris.github.io/realm-portal/ |
| Media CDN | https://media.therealmsofchaos.com/ |
| Git | `main` = `origin/main` = `653493f` (2026-10-21) |
| Publish path | Push `main`. GitHub Pages serves the repo root. No Vercel. No Node build. |
| Core catalog | 134 masters. Latest: `134_You_didnt_pick.mp4` |
| Elite catalog | 79 masters. Latest id: `079` |
| CDN HEAD 2026-10-25 | Core `134` **200** (287,667,596 bytes). Elite `073` **200** (1,646,654,142 bytes). The old Elite `073` gap is closed. |
| Teaser / thumbnail files | **None.** Poster is a text mark. List thumbs are CSS number badges. |
| Live tier truth | Make still returns `{status, link, link2}` only. `vault_grants.json` is local and gitignored, so **live Pages cannot tell Elite from Core or Inactive.** |

Ops memory for the next agent is outside git: `D:\RealmOfChaos\AgentWorkspace` (`STATE.md`, `LOG.md`).

---

## 1. System architecture and site state

Static GitHub Pages SPA. The public site is three committed files plus assets:

| Path | Bytes (local) | Last write | Role |
| --- | --- | --- | --- |
| `index.html` | 41,458 | 2026-10-21 11:32 | Page, canvas fallback, Realm Pass `fetch`, vault rooms, feed sort |
| `styles.css` | 23,494 | 2026-10-21 10:41 | Glass, Suicide Squad headers, vault rail, Elite upsell |
| `vault_catalog.json` | 53,626 | 2026-10-21 11:32 | 134 Core + 79 Elite CDN URLs. `generated_at` `2026-10-21T19:32:13Z` |
| `CNAME` | 22 | 2026-10-16 | Single line: `therealmsofchaos.com` |
| `vault_grants.json` | 7,864 | 2026-10-21 | **Gitignored.** Local Identity Bridge overlay. Not on Pages. |

Also committed and used by the page: `SuicideSquadFont-v5jA.ttf`, `Images/` (logo + tier crests), `assets/hero loop.mp4` (local copy only; the live `<video>` does not use it).

### `index.html`

- Canonical / `og:url`: `https://therealmsofchaos.com/`
- Hero `src`: `https://media.therealmsofchaos.com/hero%20loop.mp4`
- Stylesheet cache-bust: `styles.css?v=vault-index`
- Catalog fetch cache-bust: `vault_catalog.json?v=feed-134`
- Realm Pass posts `{ email }` to the Make hook already in the file: `https://hook.us2.make.com/5ln8byxwiwj7mtknejixwxsuvmf2y9ji`
- Rooms: `#vaults` → `#core-vault` / `#elite-vault`. HTML5 players `#core-video` / `#elite-video`.
- Session key: `sessionStorage` `roc-vault-access` (`core` and/or `elite`).

### `styles.css`

Dark glass layout. `@font-face` “Suicide Squad” from `SuicideSquadFont-v5jA.ttf` on headers and `.btn`. Brackets in button copy must stay stripped; that font turns `[ ]` into decorative glyphs. Vault rails scroll. `.vault.is-teaser` blurs and dims the Elite list for a Core-only pass. Elite upsell is a glass modal.

### `vault_catalog.json`

```text
cdn_base: https://media.therealmsofchaos.com
core:  134 objects, ids 001 → 134, last file 134_You_didnt_pick.mp4
elite:  79 objects, ids 001 → 079
```

Each row: `id`, `file_name`, `title`, `cdn_url`, `bytes`. The browser sorts by numeric `id` descending at render time. The JSON itself stays birth order.

### `vault_grants.json`

Present on this machine. Gitignored in `.gitignore` (`vault_grants.json` and `Bunny Videos/`). Shape:

```text
{ source, updated: "2026-10-21", members: { <email>: { tier, status } } }
```

84 member records. Counts only (no addresses in this report):

| Tier | Count |
| --- | --- |
| unset | 57 |
| Elite Breaker | 12 |
| Core Addict | 7 |
| Goon Initiate | 6 |
| Broken Mind | 1 |
| Bouchard | 1 |

| Status | Count |
| --- | --- |
| active | 28 |
| inactive | 24 |
| unset | 32 |

The page fetches this file on load. On GitHub Pages the fetch 404s, `identityMap` stays `{}`, and a successful Make reply with no `tier` is treated as **Core only**. Local preview (`python -m http.server`) is the only place the overlay applies. Do not commit this file.

### `CNAME`

`therealmsofchaos.com` — GitHub Pages custom domain. DNS for the apex points at Pages. `media.therealmsofchaos.com` is the Bunny pull-zone hostname, not a Pages host.

---

## 2. Asset indexing and Bunny.net CDN pipeline

### Zones

| Piece | Value |
| --- | --- |
| Pull zone | `realm-vault` |
| Public host | `https://media.therealmsofchaos.com` |
| Storage zone | `realm-vault-media` |
| Credentials | `Bunny Videos/Bunny Info/bunny_token.txt` (gitignored). Not copied here. |

### Dropzones

| Local | Remote | On disk 2026-10-25 |
| --- | --- | --- |
| `Bunny Videos/Core` | `/episodes/core/` | 134 `.mp4`, all prefixed, none waiting |
| `Bunny Videos/Elite` | `/episodes/elite/` | 79 `.mp4`, all prefixed, none waiting |
| `Bunny Videos/Teasers` | `/teasers/` | **empty** |
| zone root | `hero loop.mp4` | live hero |

`Bunny Videos/` is gitignored: masters, tokens, Identity Bridge PDF, and `upload_manifest.json` stay off GitHub.

### How a new file gets a name

`batch_index_veblen_assets.py` (portal root, **still untracked**) scans Core and Elite.

- Already-prefixed files are left alone. Renaming a live object would break its CDN URL.
- Unprefixed media gets the next integer: `NNN_Sanitized_Stem.mp4`.
- Prefix regex is `\d{3,}_` (4 digits are allowed when the count passes 999).
- Sanitize: spaces → `_`, `&` → `and`, other characters stripped.
- The number is **birth order**, not display order.

**Next prefixes:** Core `135_`. Elite `080_`.

The script docstring still says “Next Core = 134”. That line is stale. `134` is already live.

### How a file reaches the edge

`Bunny Videos/Bunny Info/bunny_edge_uploader.py` (gitignored with the folder):

1. Skip any Core/Elite file that lacks a numeric prefix.
2. SHA256 the file. Skip if the manifest already has `SUCCESS` for the same hash / size.
3. HTTPS PUT to Bunny Storage (`AccessKey` = storage password). Retries on failure.
4. Append the CDN URL to `upload_manifest.json`.

`--tier core|elite|teasers` and `--only <filename>` exist. Core `134` was uploaded that way on 2026-10-21 (`planned=1 uploaded=1 failed=0`).

**Standing order:** large drops go through the Bunny dashboard. The Python PUT is for one file, audit, or repair. A Core bulk script pass previously took ~9 hours; dashboard remainder was ~30 minutes.

### Thumbnails

There is no thumbnail indexer and no thumbnail folder on the CDN.

| Surface | What it is today |
| --- | --- |
| List row | CSS badge with the id + title text. Not an image. |
| Idle poster | `<span>{id}</span>` + `TEASER LOOP // FUTURE` |
| Reserved later | `Bunny Videos/Teasers/` → `/teasers/core/{id}.webp\|mp4` and `/teasers/elite/{id}.webp\|mp4` |

Do not put teaser copy back into list HTML. That leaked on 2026-10-21 and painted every row as one glued string.

### Playback URLs

Catalog URLs are public pull-zone paths. There is no Bunny token auth and no signed URL. Anyone with `vault_catalog.json` (it is in the public repo) can request a master directly.

---

## 3. Active features and Veblen vaults

### Patreon ladder (new tab)

Slug `Realm0fChaos` (zero, not the letter O).

| Tier | Button | `rid` |
| --- | --- | --- |
| Goon Initiate $5/mo | BECOME INITIATE | `26725413` |
| Core Addict $15/mo | CLAIM CORE ACCESS | `26725428` |
| Elite Breaker $25/mo | ENTER THE DESCENT | `26725442` |
| Broken Mind $50/mo | SUBMIT CONFESSION | `26725449` |
| Goddess’s Personal Disciple $500 / 14-day | PAY TRIBUTE | `28546520` |

### Realm Pass (email gate)

1. Browser POSTs `{ email }` to Make.
2. If `vault_grants.json` loaded, that record wins: `inactive` → miss; tier string → room.
3. Otherwise the Make JSON is unwrapped. `link` / `link2` are Telegram invites and are **not** room keys.
4. No declared tier on a successful lookup → **Core only**.
5. `Elite Breaker` / `Broken Mind` / Disciple → both rooms. `Goon Initiate` → upgrade notice, no vault.
6. Buttons are in-page `ENTER CORE VAULT` / `ENTER ELITE VAULT`. They are not outbound invite links.
7. Each claim resets `roc-vault-access` before writing the new grant.

### Player

- Feed label: `CORE FEED // N FILES // NEWEST FIRST` (Elite the same).
- Sort: highest `id` first. Poster id updates to the first row.
- Click sets `video.src` to `episode.cdn_url` and calls `play()`. Progressive MP4, `playsinline`, `preload=metadata`.
- Core without a pass: room stays airlocked and routes to Realm Pass.
- Elite without an Elite grant: glass teaser (blur, padlock). Click opens the upsell and does **not** set `video.src`. CTA: **UPGRADE TO ELITE VIP $25** → Patreon `rid=26725442`.
- Elite with a grant: same HTML5 path as Core, from `/episodes/elite/`.

Goddess signed the live rooms off on 2026-10-21, including mobile, before Core `134` was added. `134` was then pushed the same day (`653493f`).

---

## 4. Logged history and operations

Git history on `main` (newest first):

| Commit | Date | Subject |
| --- | --- | --- |
| `653493f` | 2026-10-21 | feat: put Core 134 at the top of the vault feed |
| `04ac2a1` | 2026-10-21 | fix: keep teaser placeholder on player poster, not episode index |
| `713a321` | 2026-10-21 | feat: deploy live Veblen vault rooms and bifurcated tier airlock |
| `e485e73` | 2026-10-16 | feat: bind therealmsofchaos.com and media CDN hero loop |
| `5542e83` | 2026-10-16 | feat: bind Bunny CDN video loop and update social meta tags |
| `5b94533` | 2026-10-16 | feat: initialize Realm portal static airlock site |

Working tree at report time: clean against `origin/main` except untracked `batch_index_veblen_assets.py`. This report is new and is not committed.

### What those commits mean

- **2026-10-16:** static airlock, Patreon ladder, Bunny hero on the custom domain.
- **2026-10-21 morning:** Core 133/133 and Elite masters on storage. Bulk Python PUT abandoned for dashboard drops. Identity Bridge overlay built locally after Make could not tell Inactive Elite from Active Elite.
- **`713a321`:** vault rooms + catalog went live. Telegram buttons removed from the grant UI.
- **`04ac2a1`:** list rows are id + title. `TEASER LOOP // FUTURE` stays on the player poster.
- **`653493f`:** `134_You_didnt_pick.mp4` in the catalog; both rails sort newest-first.

Full narrative log: `D:\RealmOfChaos\AgentWorkspace\LOG.md`.  
Day file: `D:\RealmOfChaos\AgentWorkspace\logs\2026-10-21.md`.  
Last product sitrep (now behind this report on the `073` CDN check): `Bunny Videos/MotherBase_Sitrep_Site_Live_2026-10-21.md`.

### Open leftovers

1. Make must return `tier` and `patron_status` or live Elite / Inactive stays wrong.
2. 57 overlay rows have no tier. Even locally those fall through to Core-only if status is not `inactive`.
3. Teaser loops and real thumbnails are not built.
4. Masters are public CDN URLs.
5. `batch_index_veblen_assets.py` is untracked. Its “next Core = 134” comment is stale.
6. Local `assets/hero loop.mp4` is still in the repo.

---

## 5. Integration readiness

Ogun can read Mother Base execution plans from both drop points.

| Drop | Path | State on 2026-10-25 |
| --- | --- | --- |
| Portal plan | `D:\RealmOfChaos\Veblen_Portal\CURRENT_MOTHERBASE_BUILD_PLAN.md` | **Not present.** Will be read on the next pass when Mother Base writes it. |
| Airlock requests | `D:\MotherBase\06_Swarm_Airlock\Ogun\requests\` | **Folder exists. Empty.** |
| Node registry | `D:\MotherBase\03_Workspace_Config\nodes_registry.json` | Node 5 Ogun: workspace `D:\RealmOfChaos\Veblen_Portal`, mirror `D:\MotherBase\06_Swarm_Airlock\Ogun`, status ACTIVE. |
| This report | portal root + airlock copy | Written this pass. |

Read order on the next Mother Base ticket:

1. `CURRENT_MOTHERBASE_BUILD_PLAN.md` in the portal root, if it exists.
2. Every file in `D:\MotherBase\06_Swarm_Airlock\Ogun\requests\`.
3. `D:\RealmOfChaos\AgentWorkspace\STATE.md` and the newest `LOG.md` block, so a plan does not repeat a finished deploy.

Ogun will not commit `vault_grants.json`, `Bunny Videos/`, tokens, or invite URLs. A plan that asks for a live Elite/Inactive fix is blocked on Make JSON (`tier`, `patron_status`) unless Goddess orders a different gate. Large new media still goes to the Bunny dashboard; one-file repair can use `bunny_edge_uploader.py --only`.

**Node 5 is online and holding for the next plan.**
