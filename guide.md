### Set up automatic vote updates with Cronitor

After this PR is merged, the repository owner can use Cronitor to trigger **Update skill votes** every five minutes. This setup must target the **upstream repository**, not a contributor’s fork.

1. [Sign up for Cronitor](https://cronitor.io/sign-up) using **Sign up with GitHub**. This signs you in to Cronitor; a separate GitHub token is still required for the check.
2. [Create a fine-grained GitHub token](https://github.com/settings/personal-access-tokens/new). Set the resource owner to the owner of this repository, select **only this repository**, and grant **Repository permissions → Actions → Read and write**. Copy the token when GitHub displays it.
3. Open the [Cronitor monitors page](https://cronitor.io/app/checks), create a new **Check**, and select **HTTP** as the request type. If prompted, sign in first. Configure the request using the settings below.

   | Setting | Value |
   | --- | --- |
   | Title | `Update skill votes` |
   | Method | `POST` |
   | Endpoint | `https://api.github.com/repos/OWNER/REPOSITORY/actions/workflows/update-skill-votes.yml/dispatches` |
   | Interval | Every 5 minutes |
   | Request region | One region |

   Add these request headers:

   ```text
   Authorization: Bearer YOUR_GITHUB_TOKEN
   Accept: application/vnd.github+json
   Content-Type: application/json
   ```

   Add this request body, replacing `main` if the repository has a different default branch:

   ```json
   {"ref":"main","inputs":{"sync_discussions":"true"}}
   ```

4. Replace `OWNER` and `REPOSITORY` in the URL, save the check, and send one test request. Confirm a new run appears under **GitHub → Actions → Update skill votes** and finishes successfully.

**Important:** Keep the token only in Cronitor. Never put it in the PR, repository files, or GitHub Pages. `Authorization` must include `Bearer ` before the token. A successful HTTP response confirms GitHub accepted the dispatch; check the Action run separately for processing errors. Renew the token before it expires.

[GitHub workflow-dispatch API reference](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event)