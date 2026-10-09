# Community Voting Rollout

Use this checklist after the community voting pull request is merged.

## 1. Enable GitHub features

1. Open the repository on GitHub.
2. Go to **Settings -> General -> Features**.
3. Enable **Discussions**.
4. Go to the **Discussions** tab.
5. Create a discussion category named exactly:

```text
Skill Votes
```

6. Go to **Settings -> Pages**.
7. Set **Source** to **GitHub Actions** and save.
8. After merging the Pages workflow, run **Actions -> Deploy community page -> Run workflow** once.

The deployment workflow publishes the `/docs` folder and generates the contributor list without committing it. It also runs on pushes to `main` and after vote data changes.

The dashboard will be available at:

```text
https://OWNER.github.io/REPOSITORY/
```

## 2. Allow the workflow to update files

1. Go to **Settings -> Actions -> General**.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Save.

The voting workflow needs write access to:

- create missing vote discussions
- update `RANKING.md`
- update `docs/votes.json`
- update `docs/vote-discussions.json`

## 3. Run the first sync

1. Go to **Actions**.
2. Open **Update skill votes**.
3. Click **Run workflow**.
4. Keep `sync_discussions` enabled.
5. Run it on the default branch.

Expected result:

- one `Vote: skill-name` discussion is created for each root-level skill
- `docs/vote-discussions.json` stores the official discussion IDs
- `RANKING.md` is updated
- `docs/votes.json` is updated for the GitHub Pages dashboard

## 4. Configure Cronitor

Create a Cronitor **HTTP Check**, not a Job monitor or alert webhook. Set its interval to `every 5 minutes` and configure this request using [Cronitor's HTTP Check settings](https://cronitor.io/docs/monitors-api):

```text
Method: POST
URL: https://api.github.com/repos/OWNER/REPOSITORY/actions/workflows/update-skill-votes.yml/dispatches
Authorization: Bearer YOUR_GITHUB_TOKEN
Accept: application/vnd.github+json
Content-Type: application/json
```

```json
{"ref":"DEFAULT_BRANCH","inputs":{"sync_discussions":"true"}}
```

Replace `OWNER`, `REPOSITORY`, and `DEFAULT_BRANCH` with this repository's values. Create a fine-grained GitHub token limited to this repository with **Actions: write** permission for [GitHub's workflow dispatch API](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event), and put it only in Cronitor's request headers. Do not add it to this repository or the Pages frontend. Renew it before it expires.

Send a test request from Cronitor and confirm an **Update skill votes** run appears in GitHub Actions. A successful HTTP check means GitHub accepted the dispatch; confirm the Action itself succeeds separately. Cronitor must be configured for each fork or upstream repository that needs automatic runs.

## 5. Smoke test the public flow

1. Open the GitHub Pages dashboard.
2. Confirm all skills are visible.
3. Search for a skill by name.
4. Open a skill's **Vote on GitHub** link.
5. Upvote the discussion.
6. Wait for Cronitor's next check and confirm the resulting Action succeeds.
7. Confirm `docs/votes.json` and `RANKING.md` contain the updated count.
8. Refresh the dashboard and confirm the displayed count changed.

## 6. Announce to the community

Suggested announcement:

```md
We launched Skillpper community voting.

Open the leaderboard, pick the skills you use, and upvote each skill's GitHub Discussion.

Leaderboard: https://OWNER.github.io/REPOSITORY/

Votes help us understand which skills are useful, which ones need improvement, and what the community wants next.
```

## 7. Ongoing maintenance

- New skills are picked up automatically from root-level `*/SKILL.md` files.
- Cronitor requests a workflow run every five minutes; GitHub Actions may take additional time to complete it.
- Missing official vote discussions are created automatically.
- Copied vote markers in community-created discussions are ignored.
- The trusted discussion mapping is stored in `docs/vote-discussions.json`.

If a skill is renamed, check the next workflow run and confirm the new skill has a vote discussion.

If a discussion is deleted manually, remove the matching entry from `docs/vote-discussions.json` and rerun the workflow with `sync_discussions` enabled.

## 8. Troubleshooting

If the workflow does not run automatically:

- confirm the workflow file is on the default branch
- confirm Actions are enabled
- confirm the Cronitor HTTP Check is enabled and its latest POST succeeded
- confirm the token has **Actions: write** access and has not expired
- confirm the Cronitor URL targets the correct repository and `ref` names its default branch

If the workflow fails to create discussions:

- confirm Discussions are enabled
- confirm the category is named `Skill Votes`
- confirm workflow permissions are **Read and write permissions**

If the dashboard loads but shows old data:

- confirm `docs/votes.json` was updated by the workflow
- confirm **Deploy community page** succeeded after the vote update; unchanged vote data does not trigger a new deployment
- confirm **Settings -> Pages -> Source** is **GitHub Actions**
