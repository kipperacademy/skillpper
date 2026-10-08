const state = {
  skills: [],
  repository: null,
};

const skillList = document.querySelector("#skillList");
const emptyState = document.querySelector("#emptyState");
const searchInput = document.querySelector("#searchInput");
const template = document.querySelector("#skillCardTemplate");
const totalVotes = document.querySelector("#totalVotes");
const totalSkills = document.querySelector("#totalSkills");
const updatedAt = document.querySelector("#updatedAt");
const syncButton = document.querySelector("#syncButton");
const repositoryLink = document.querySelector("#repositoryLink");

function inferRepositoryFromPagesUrl() {
  const host = window.location.hostname;
  const owner = host.endsWith(".github.io") ? host.replace(".github.io", "") : "";
  const repo = window.location.pathname.split("/").filter(Boolean)[0] || "";
  return owner && repo ? `${owner}/${repo}` : null;
}

function workflowUrl(repository) {
  return `https://github.com/${repository}/actions/workflows/update-skill-votes.yml`;
}

function repositoryUrl(repository) {
  return `https://github.com/${repository}`;
}

function relativeSkillUrl(skill) {
  const repository = state.repository;
  if (repository) {
    return `${repositoryUrl(repository)}/blob/HEAD/${skill}/SKILL.md`;
  }
  return `../${skill}/SKILL.md`;
}

function formatDate(value) {
  if (!value) return "Waiting for vote data";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Vote data loaded";
  return `Updated ${date.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  })}`;
}

function voteLabel(count) {
  return count === 1 ? "1 vote" : `${count} votes`;
}

function configureLinks(repository) {
  if (!repository) return;
  syncButton.href = workflowUrl(repository);
  syncButton.removeAttribute("aria-disabled");
  syncButton.title = "Requires write access to the repository";

  repositoryLink.href = repositoryUrl(repository);
  repositoryLink.hidden = false;
}

function renderSkills(skills) {
  skillList.replaceChildren();
  skills.forEach((skill) => {
    const node = template.content.cloneNode(true);
    const card = node.querySelector(".skill-card");
    const rank = node.querySelector(".rank");
    const title = node.querySelector("h3");
    const description = node.querySelector("p");
    const votePill = node.querySelector(".vote-pill");
    const discussionLink = node.querySelector('[data-kind="discussion"]');
    const sourceLink = node.querySelector('[data-kind="source"]');

    card.dataset.skill = skill.skill;
    rank.textContent = skill.rank;
    title.textContent = skill.skill;
    description.textContent = skill.description;
    votePill.textContent = voteLabel(skill.votes);

    if (skill.discussion_url) {
      discussionLink.href = skill.discussion_url;
    } else {
      discussionLink.textContent = "Discussion pending";
      discussionLink.setAttribute("aria-disabled", "true");
    }
    sourceLink.href = relativeSkillUrl(skill.skill);

    skillList.append(node);
  });
  emptyState.hidden = skills.length > 0;
}

function applySearch() {
  const query = searchInput.value.trim().toLowerCase();
  const filtered = state.skills.filter((skill) => {
    return `${skill.skill} ${skill.description}`.toLowerCase().includes(query);
  });
  renderSkills(filtered);
}

async function loadVotes() {
  try {
    const response = await fetch("votes.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`Vote data returned ${response.status}`);
    const data = await response.json();

    state.skills = Array.isArray(data.skills) ? data.skills : [];
    state.repository = inferRepositoryFromPagesUrl() || data.repository || null;

    totalVotes.textContent = data.total_votes ?? 0;
    totalSkills.textContent = data.total_skills ?? state.skills.length;
    updatedAt.textContent = formatDate(data.updated_at);
    configureLinks(state.repository);
    renderSkills(state.skills);
  } catch (error) {
    updatedAt.textContent = "Could not load vote data";
    emptyState.textContent = "The dashboard could not load votes.json.";
    emptyState.hidden = false;
  }
}

searchInput.addEventListener("input", applySearch);
loadVotes();
