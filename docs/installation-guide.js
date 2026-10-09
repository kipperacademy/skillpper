const agents = [
  { name: 'Claude Code', icon: 'claude-color' },
  { name: 'OpenAI Codex', icon: 'openai' },
  { name: 'GitHub Copilot', icon: 'github-copilot' }, // Uses its standard colored SVG
  { name: 'Cursor', icon: 'cursor' }, // Multi-color by default
  { name: 'Gemini CLI', icon: 'gemini-color' }, // Uses Google's multi-color logo
  { name: 'Windsurf', icon: 'windsurf' }, // Multi-color by default
  { name: 'DeepSeek', icon: 'deepseek-color' },
  { name: 'Mistral', icon: 'mistral-color' },
];

const agentTrack = document.querySelector('#agentTrack');
const agentMarquee = document.querySelector('#agentMarquee');
const copyButton = document.querySelector('#copyInstallCommand');
const installCommand = document.querySelector('#installCommand');
const copyStatus = document.querySelector('#copyStatus');

function createAgentGroup(isDuplicate = false) {
  const group = document.createElement('div');
  group.className = 'agent-group';
  group.setAttribute('role', 'list');
  if (isDuplicate) group.setAttribute('aria-hidden', 'true');

  agents.forEach((agent) => {
    const item = document.createElement('div');
    item.className = 'agent-item';
    item.setAttribute('role', 'listitem');

    const icon = document.createElement('img');
    icon.src = `https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@latest/icons/${agent.icon}.svg`;
    icon.alt = '';
    icon.loading = 'lazy';
    icon.addEventListener('error', () => icon.remove());

    const label = document.createElement('span');
    label.textContent = agent.name;
    item.append(icon, label);
    group.append(item);
  });

  return group;
}

agentTrack.append(createAgentGroup(), createAgentGroup(true));
agentMarquee.addEventListener('focusin', () => {
  agentTrack.style.animationPlayState = 'paused';
});
agentMarquee.addEventListener('focusout', () => {
  agentTrack.style.animationPlayState = '';
});

async function copyCommand() {
  const command = installCommand.textContent.trim();
  try {
    await navigator.clipboard.writeText(command);
  } catch {
    const temporaryInput = document.createElement('textarea');
    temporaryInput.value = command;
    temporaryInput.setAttribute('readonly', '');
    temporaryInput.style.position = 'fixed';
    temporaryInput.style.opacity = '0';
    document.body.append(temporaryInput);
    temporaryInput.select();
    const copied = document.execCommand('copy');
    temporaryInput.remove();
    if (!copied) {
      copyStatus.textContent = 'Copy failed. Select the command to copy it.';
      return;
    }
  }

  const svgIcon = copyButton.querySelector('svg');

  copyButton.textContent = 'Copied';
  copyStatus.textContent = 'Installation command copied.';
  window.setTimeout(() => {
    copyButton.replaceChildren(svgIcon);
    copyStatus.textContent = '';
  }, 1800);
}

copyButton.addEventListener('click', copyCommand);
