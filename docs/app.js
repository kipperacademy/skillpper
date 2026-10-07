const state = {
  skills: [],
  repository: null,
  categories: {},
  sort: "rank",
  category: "all",
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
const categoryField = document.querySelector("#categoryField");
const categorySelect = document.querySelector("#categorySelect");
const sortSelect = document.querySelector("#sortSelect");
const themeToggle = document.querySelector("#themeToggle");

const collator = new Intl.Collator(undefined, { sensitivity: "base" });

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
    const categoryPill = node.querySelector('[data-kind="category"]');
    const discussionLink = node.querySelector('[data-kind="discussion"]');
    const sourceLink = node.querySelector('[data-kind="source"]');

    card.dataset.skill = skill.skill;
    rank.textContent = skill.rank;
    title.textContent = skill.skill;
    description.textContent = skill.description;
    votePill.textContent = voteLabel(skill.votes);

    const category = categoryFor(skill.skill);
    categoryPill.hidden = !category;
    categoryPill.textContent = category;

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

function categoryFor(skill) {
  return state.categories[skill] || "";
}

function populateCategoryFilter() {
  const categories = [...new Set(Object.values(state.categories).filter(Boolean))].sort((a, b) =>
    collator.compare(a, b)
  );
  if (categories.length === 0) {
    categoryField.hidden = true;
    return;
  }
  categoryField.hidden = false;
  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    categorySelect.append(option);
  });
}

function visibleSkills() {
  const query = searchInput.value.trim().toLowerCase();
  const filtered = state.skills.filter((skill) => {
    const matchesQuery = `${skill.skill} ${skill.description}`.toLowerCase().includes(query);
    const matchesCategory = state.category === "all" || categoryFor(skill.skill) === state.category;
    return matchesQuery && matchesCategory;
  });
  if (state.sort === "az") {
    filtered.sort((a, b) => collator.compare(a.skill, b.skill));
  } else if (state.sort === "za") {
    filtered.sort((a, b) => collator.compare(b.skill, a.skill));
  } else {
    filtered.sort((a, b) => a.rank - b.rank);
  }
  return filtered;
}

function applySearch() {
  renderSkills(visibleSkills());
}

async function fetchJson(file) {
  const response = await fetch(file, { cache: "no-store" });
  if (!response.ok) throw new Error(`${file} returned ${response.status}`);
  return response.json();
}

async function loadVotes() {
  try {
    const [data, categories] = await Promise.all([
      fetchJson("votes.json"),
      fetchJson("skill-categories.json").catch(() => ({})),
    ]);

    state.skills = Array.isArray(data.skills) ? data.skills : [];
    state.repository = data.repository || inferRepositoryFromPagesUrl();
    state.categories =
      categories && typeof categories === "object" && !Array.isArray(categories) ? categories : {};
    populateCategoryFilter();

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

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const dark = theme === "dark";
  themeToggle.setAttribute("aria-pressed", String(dark));
  themeToggle.textContent = dark ? "☀️ Light" : "🌙 Dark";
}

function toggleTheme() {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  applyTheme(next);
  try {
    window.localStorage.setItem("skillpper-theme", next);
  } catch (error) {
    // Storage unavailable: the theme still applies for this session.
  }
}

function initTheme() {
  applyTheme(document.documentElement.dataset.theme === "dark" ? "dark" : "light");
}

searchInput.addEventListener("input", applySearch);
categorySelect.addEventListener("change", () => {
  state.category = categorySelect.value;
  applySearch();
});
sortSelect.addEventListener("change", () => {
  state.sort = sortSelect.value;
  applySearch();
});
themeToggle.addEventListener("click", toggleTheme);
initTheme();
loadVotes();
