"""Read-only first-time provider and Agent1 setup guide for one SYSTEMX scope.

The provider catalog is navigation, not authentication, provider execution, or
a second agent registry. Only an explicit ``onboard bridge --apply`` may create
the fixed root AGENTS.md pointer through the separate guarded bridge helper.
"""

import shutil
from pathlib import Path

import root_coordination
import security_agent1


COMMANDS = {"onboard"}
REQUIRED = ("scripts/onboarding.py", "tests/test_onboarding.py")
ACCOUNT_CONTEXTS = ("personal", "enterprise")
SURFACES = ("cli", "vscode", "vscode-terminal", "vscode-extension",
            "codex", "codex-ide", "ide", "sdk", "cloud", "harness")
CONSUMERS = ("local-cli", "vscode-extension", "codespaces", "github-agents",
             "actions", "dependabot", "server-application", "none")
CREDENTIAL_CLASSES = ("new", "existing-test", "none")

# These are supported navigation targets, not implicitly installed workers.
# The stable IDs avoid conflating an AI model, a CLI executable, and an online
# Bot account. A selected provider's own documentation controls its real setup.
PROVIDERS = (
    {"id": "codex-cli", "name": "OpenAI Codex CLI", "kind": "cli", "executable": "codex",
     "surfaces": ("cli", "vscode", "vscode-terminal", "codex", "harness"), "lane": "agent.y",
     "execution": "task-scoped-agent-y", "reference": "https://learn.chatgpt.com/docs/codex/cli",
     "setup": ("codex --help", "agent-y providers", "agent-y prepare --help")},
    {"id": "codex-ide", "name": "OpenAI Codex IDE extension", "kind": "ide", "executable": None,
     "surfaces": ("vscode", "vscode-extension", "codex", "codex-ide"), "lane": "host-ide",
     "execution": "host-managed", "reference": "https://learn.chatgpt.com/docs/codex/ide",
     "setup": ("Review Codex IDE extension sign-in and selected workspace in the host IDE",)},
    {"id": "codex-sdk", "name": "OpenAI Codex SDK", "kind": "sdk", "executable": None,
     "surfaces": ("sdk", "harness"), "lane": "host-application",
     "execution": "application-managed", "reference": "https://learn.chatgpt.com/docs/codex-sdk",
     "setup": ("Review the TypeScript or Python Codex SDK guide and application-side authentication",
               "Keep application credentials outside portable .SYSTEMX records")},
    {"id": "openai-dot", "name": "OpenAI dot", "kind": "external-bot-reference",
     "executable": None, "surfaces": ("harness",), "lane": "agent.b",
     "execution": "offline-reference-only", "reference": "https://learn.chatgpt.com/docs/dots/getting-started",
     "setup": ("agent-beta setup --help", "agent-beta bot-add --help")},
    {"id": "grok-build", "name": "xAI Grok Build CLI", "kind": "cli", "executable": "grok",
     "surfaces": ("cli", "vscode", "vscode-terminal", "harness"), "lane": "agent.y",
     "execution": "manual-until-reviewed-adapter", "reference": "https://docs.x.ai/build/overview",
     "setup": ("grok --help", "grok login", "grok inspect")},
    {"id": "grok-bot", "name": "xAI Grok Bot reference", "kind": "external-bot-reference",
     "executable": None, "surfaces": ("harness",), "lane": "agent.b",
     "execution": "offline-reference-only", "reference": "https://docs.x.ai/grok-bot/overview",
     "setup": ("agent-beta setup --help", "agent-beta bot-add --help")},
    {"id": "muse-code", "name": "Meta Muse Code CLI", "kind": "cli", "executable": "muse",
     "surfaces": ("cli", "vscode", "vscode-terminal", "harness"), "lane": "agent.y",
     "execution": "task-scoped-agent-y", "reference": "https://dev.meta.ai/docs/muse-code",
     "setup": ("muse --version", "muse (interactive: review workspace trust and browser sign-in)",
               "agent-y providers", "agent-y prepare --help")},
    {"id": "meta-muse", "name": "Meta personal Muse reference", "kind": "external-bot-reference",
     "executable": None, "surfaces": ("harness",), "lane": "agent.b",
     "execution": "offline-reference-only", "reference": "https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent",
     "setup": ("agent-beta setup --help", "agent-beta bot-add --help")},
    {"id": "kiro-cli", "name": "Kiro CLI (formerly Amazon Q Developer CLI)", "kind": "cli",
     "executable": "kiro-cli", "surfaces": ("cli", "vscode-terminal", "harness"),
     "lane": "agent.y", "execution": "manual-until-reviewed-adapter",
     "reference": "https://kiro.dev/docs/reference/cli-commands/", "setup": ("kiro-cli version",
     "Review Kiro CLI authentication and tool approvals in the provider documentation")},
    {"id": "kiro-ide", "name": "Kiro IDE", "kind": "ide", "executable": None,
     "surfaces": ("ide",), "lane": "host-ide", "execution": "host-managed",
     "reference": "https://kiro.dev/docs/getting-started/installation/",
     "setup": ("Open the selected project in Kiro IDE and review its own sign-in and trust settings",)},
    {"id": "kiro-web", "name": "Kiro Web", "kind": "external-bot-reference",
     "executable": None, "surfaces": ("cloud",), "lane": "agent.b",
     "execution": "offline-reference-only", "reference": "https://kiro.dev/docs/web/setup/",
     "setup": ("Review Kiro Web account and GitHub app repository permissions externally",
               "agent-beta bot-add --help")},
    {"id": "aws-cli", "name": "AWS CLI", "kind": "cloud-cli", "executable": "aws",
     "surfaces": ("cli", "vscode-terminal"), "lane": "host-account",
     "execution": "manual-cloud-command-only",
     "reference": "https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html",
     "setup": ("aws --version", "Review IAM Identity Center profile and region outside .SYSTEMX",
               "aws sts get-caller-identity --profile PROFILE (only after a human selects the profile)")},
    {"id": "claude-code", "name": "Anthropic Claude Code CLI", "kind": "cli",
     "executable": "claude", "surfaces": ("cli", "vscode", "vscode-terminal", "harness"),
     "lane": "agent.y", "execution": "manual-until-reviewed-adapter",
     "reference": "https://code.claude.com/docs/en/cli-reference",
     "setup": ("claude --version", "Review Claude Code sign-in and project instruction settings")},
    {"id": "opencode-cli", "name": "OpenCode CLI", "kind": "cli", "executable": "opencode",
     "surfaces": ("cli", "vscode", "vscode-terminal", "harness"), "lane": "agent.y",
     "execution": "manual-until-reviewed-adapter",
     "reference": "https://dev.opencode.ai/v2/docs/cli",
     "setup": ("opencode --version", "Review OpenCode provider login and background service behavior")},
    {"id": "blackbox-cli", "name": "BLACKBOX AI CLI", "kind": "cli",
     "executable": "blackbox", "surfaces": ("cli", "vscode", "vscode-terminal", "harness"),
     "lane": "agent.y", "execution": "manual-until-reviewed-adapter",
     "reference": "https://docs.blackbox.ai/features/blackbox-cli/commands-reference",
     "setup": ("blackbox help", "Review BLACKBOX CLI provider configuration outside .SYSTEMX")},
    {"id": "gemini-cli", "name": "Google Gemini CLI", "kind": "cli", "executable": "gemini",
     "surfaces": ("cli", "vscode", "vscode-terminal", "harness"), "lane": "agent.y",
     "execution": "manual-until-reviewed-adapter",
     "reference": "https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/cli-reference.md",
     "setup": ("gemini --version", "Review Google account, API key, or Vertex AI authentication separately")},
    {"id": "cursor-agent", "name": "Cursor Agent CLI", "kind": "cli",
     "executable": None, "surfaces": ("cli", "vscode-terminal", "harness"),
     "lane": "agent.y", "execution": "manual-until-reviewed-adapter",
     "reference": "https://cursor.com/docs/cli/installation",
     "setup": ("Confirm manually that the generic 'agent' command belongs to Cursor",
               "agent --version", "Review Cursor CLI login and write permissions")},
    {"id": "aider", "name": "Aider CLI", "kind": "cli", "executable": "aider",
     "surfaces": ("cli", "vscode-terminal", "harness"), "lane": "agent.y",
     "execution": "manual-until-reviewed-adapter",
     "reference": "https://aider.chat/docs/usage.html",
     "setup": ("aider --version", "Review model-provider keys and automatic commit defaults")},
    {"id": "copilot-cli", "name": "GitHub Copilot CLI", "kind": "cli", "executable": "copilot",
     "surfaces": ("cli", "vscode", "vscode-terminal", "harness"), "lane": "agent.y",
     "execution": "task-scoped-agent-y", "reference": "https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli",
     "setup": ("copilot --help", "agent-y providers", "agent-y prepare --help")},
    {"id": "configured-cli", "name": "Reviewed configured CLI adapter", "kind": "cli",
     "executable": None, "surfaces": ("cli", "vscode-terminal", "harness"), "lane": "agent.y",
     "execution": "task-scoped-reviewed-adapter", "reference": "docs/AGENT-Y.md",
     "setup": ("agent-y prepare --help", "agent-y run --help")},
)
PROVIDER_IDS = frozenset(item["id"] for item in PROVIDERS)
LIMIT = ("Local setup navigation and filename/key-name inventory only. Installed CLI name does "
         "not prove authentication, provider rights, model availability, or safe execution. "
         "No secret values, provider calls, service installation, or agent run.")


def _selection(value, choices, label):
    if value is not None and (not isinstance(value, str) or value not in choices):
        raise ValueError("Unknown " + label)
    return value


def _catalog(provider=None, surface=None):
    _selection(provider, PROVIDER_IDS, "provider")
    _selection(surface, SURFACES, "surface")
    selected = []
    for item in PROVIDERS:
        if provider is not None and item["id"] != provider:
            continue
        if surface is not None and surface not in item["surfaces"]:
            continue
        selected.append({"id": item["id"], "name": item["name"], "kind": item["kind"],
                         "surfaces": list(item["surfaces"]), "lane": item["lane"],
                         "execution": item["execution"], "reference": item["reference"],
                         "installedNameOnly": (shutil.which(item["executable"]) is not None
                                               if item["executable"] else None)})
    return selected


def _agent1(root):
    state = security_agent1.status(root)
    registration = state["registration"]
    return {"configured": state["configured"], "registered": registration["registered"],
            "roleConflict": registration["conflict"],
            "missingQuestionCount": len(state["missingQuestions"]), "mode": "warning-only"}


def view(root, *, mode="status", provider=None, surface=None, account_context=None,
         credential_consumer=None, credential_class=None, env_file=None):
    """Return selected-scope setup metadata without changing any record or host setting."""
    if mode not in {"status", "plan"}:
        raise ValueError("Unknown onboarding view")
    _selection(account_context, ACCOUNT_CONTEXTS, "account context")
    _selection(credential_consumer, CONSUMERS, "credential consumer")
    _selection(credential_class, CREDENTIAL_CLASSES, "credential class")
    if credential_consumer == "none" and credential_class not in {None, "none"}:
        raise ValueError("A no-credential consumer cannot select a key class")
    if mode == "plan" and credential_class is None and credential_consumer is not None:
        # Advice only; no key is created or requested. An unselected consumer
        # must not appear to recommend creating a credential.
        credential_class = "none" if credential_consumer == "none" else "new"
    selected = _catalog(provider, surface)
    if provider is not None and not selected:
        raise ValueError("Selected provider does not support that surface")
    root = Path(root)
    roster = root_coordination.roster(root)
    result = {"schemaVersion": 1, "mode": mode,
              "scope": "root" if root.name == ".SYSTEMX" else "project",
              "selection": {"provider": provider, "surface": surface,
                            "accountContext": account_context,
                            "credentialConsumer": credential_consumer,
                            "credentialClass": credential_class},
              "providers": selected, "roster": {"counts": roster["counts"],
                                                  "sourceRevision": roster["sourceRevision"]},
              "toolchains": {"options": roster["toolchainOptions"],
                             "portableIO": roster["portableIO"],
                             "nativeHostBindingsInstalled": roster["nativeHostBindingsInstalled"]},
              "agent1": _agent1(root), "envInventory": None,
              "authenticated": False, "accessGranted": False, "runtimeStarted": False,
              "valuesReturned": False, "executed": False, "limit": LIMIT}
    if env_file is not None:
        # Agent 1 owns no-follow, bounded dotenv parsing and Git tracking.
        result["envInventory"] = security_agent1.env_inventory(root, env_file)
    if mode == "plan":
        if surface in {"vscode", "codex"}:
            result["surfaceBoundary"] = ("A CLI in VS Code's terminal and a VS Code extension "
                                         "use their own provider login and permissions; choose "
                                         "vscode-terminal, vscode-extension, or codex-ide "
                                         "before supplying credentials.")
        result["questions"] = [
            {"id": "accountContext", "prompt": "Personal or enterprise workspace?",
             "choices": list(ACCOUNT_CONTEXTS), "selected": account_context},
            {"id": "surface", "prompt": "Which entry point will the human or agent use?",
             "choices": list(SURFACES), "selected": surface},
            {"id": "provider", "prompt": "Which provider surface is intended?",
             "choices": sorted(PROVIDER_IDS), "selected": provider},
            {"id": "credentialConsumer", "prompt": "Where will a credential be consumed?",
             "choices": list(CONSUMERS), "selected": credential_consumer},
            {"id": "credentialClass", "prompt": "If needed, new credential or existing test credential?",
             "choices": list(CREDENTIAL_CLASSES), "selected": credential_class},
        ]
        result["nextSteps"] = [
            "agent-1 status",
            "agent-1 setup --help",
            "agent-1 env-inventory --env-file PATH (only if an existing file is selected)",
            "agent-1 env-sanitize --env-file PATH (preview names-only example)",
            "root roster",
        ]
        if root.name == ".SYSTEMX":
            result["nextSteps"].append(
                "onboard bridge (preview a single AGENTS.md pointer before any apply)")
        else:
            result["nextSteps"].append(
                "Select the outer .SYSTEMX scope for onboard bridge; a child .SYSTEMXP has no root instruction bridge")
        if provider is not None:
            result["providerNextSteps"] = list(next(item["setup"] for item in PROVIDERS
                                                       if item["id"] == provider))
        if credential_consumer == "actions":
            result["credentialBoundary"] = ("GitHub Actions is disabled for the upstream dotSYSTEMX "
                                            "repository; a selected project's state may differ and must "
                                            "be verified externally. An Actions secret is never a local "
                                            "CLI or VS Code credential. No key is created or copied here.")
        elif credential_consumer in {"github-agents", "codespaces", "dependabot"}:
            result["credentialBoundary"] = ("Use the selected GitHub consumer's own secret scope "
                                            "and verify it externally; it does not populate a local .env.")
        elif credential_consumer in {"local-cli", "vscode-extension", "server-application"}:
            result["credentialBoundary"] = ("Prefer provider login or an approved OS credential store. "
                                            "If a key is needed, prefer a newly issued key; treat an "
                                            "existing key as test-only until rotation is reviewed. "
                                            "A server application must use its own approved secret "
                                            "destination. No project .env value is required by this guide.")
        else:
            result["credentialBoundary"] = "No credential destination selected. No key is created or copied."
        result["credentialReview"] = {
            "new": "If key-based access is needed, issue a new scoped key; no key is created here.",
            "existing-test": "Treat an existing key as test-only; review tracked history and rotate before production use.",
            "none": "No credential is selected or created.",
            None: "Select a credential consumer before choosing a key class.",
        }[credential_class]
    return result


def format_text(result):
    """Render the already sanitized packet for a first-time human reader."""
    if "contentSha256" in result and "preview" in result:
        lines = [".SYSTEMX instruction bridge", "Target: " + result["path"],
                 "State: " + result["state"],
                 "Preview SHA-256: " + result["contentSha256"],
                 "Applied: " + ("yes" if result["applied"] else "no"),
                 "", "Proposed content:", result["preview"].rstrip(), "",
                 result["limit"]]
        return "\n".join(lines)
    agent_count = result["roster"]["counts"]["registeredAgents"]
    lines = [".SYSTEMX first-time setup: " + result["mode"],
             "Scope: " + result["scope"],
             "Agent1: " + ("configured" if result["agent1"]["configured"] else "needs setup") +
             " (warning-only; " + str(result["agent1"]["missingQuestionCount"]) + " open questions)",
             "Agent 0 roster: " + str(result["roster"]["counts"]["rows"]) + " rows; " +
             str(agent_count) + " registered agent" + ("" if agent_count == 1 else "s"),
             "Toolchains for explicit host I/O: " + ", ".join(result["toolchains"]["options"]),
             "Native host bindings installed: no",
             "", "Provider surfaces (installed is a name check only):"]
    for item in result["providers"]:
        installed = ("manual/host" if item["installedNameOnly"] is None else
                     "name found" if item["installedNameOnly"] else "name absent")
        lines.append("- " + item["id"] + ": " + item["name"] + " | " + item["lane"] +
                     " | " + installed + " | " + item["execution"])
        lines.append("  Reference: " + item["reference"])
    env = result["envInventory"]
    if env is not None:
        lines += ["", "Selected dotenv file: " + env["source"],
                  "Key names only: " + (", ".join(env["names"]) if env["names"] else "none"),
                  "Duplicate names: " + (", ".join(env["duplicateNames"]) if env["duplicateNames"] else "none"),
                  "Unsupported line numbers: " +
                  (", ".join(str(number) for number in env["unsupportedLineNumbers"])
                   if env["unsupportedLineNumbers"] else "none"),
                  "Tracked by Git: " + str(env["trackedByGit"]).lower()]
        if env["trackingWarning"]:
            lines.append("Tracking check: " + env["trackingWarning"])
    if result["mode"] == "plan":
        lines += ["", "Setup choices:"]
        for item in result["questions"]:
            lines.append("- " + item["prompt"] + " " +
                         ("[selected: " + item["selected"] + "]" if item["selected"] else
                          "[choose: " + ", ".join(item["choices"]) + "]"))
        if result.get("surfaceBoundary"):
            lines += ["", result["surfaceBoundary"]]
        lines += ["", "Next commands:"]
        lines += ["- " + command for command in result["nextSteps"]]
        lines += ["- " + command for command in result.get("providerNextSteps", [])]
        lines += ["", result["credentialBoundary"], result["credentialReview"]]
    lines += ["", result["limit"]]
    return "\n".join(lines)


def add_cli(subparsers, scope=None):
    scope = scope or (lambda parser: parser)
    parent = subparsers.add_parser("onboard", help="first-time provider, Agent1, and env security navigation")
    actions = parent.add_subparsers(dest="onboard_action", required=True)
    for name in ("status", "plan"):
        command = scope(actions.add_parser(name, help="read-only onboarding " + name))
        command.add_argument("--provider", choices=sorted(PROVIDER_IDS))
        command.add_argument("--surface", choices=SURFACES)
        command.add_argument("--account-context", choices=ACCOUNT_CONTEXTS)
        command.add_argument("--credential-consumer", choices=CONSUMERS)
        command.add_argument("--credential-class", choices=CREDENTIAL_CLASSES)
        command.add_argument("--env-file", help="explicit contained dotenv path; values are never returned")
        command.add_argument("--format", choices=("text", "json"), default="text")
    command = scope(actions.add_parser("bridge", help="preview or create the fixed project AGENTS.md pointer"))
    command.add_argument("--apply", action="store_true")
    command.add_argument("--expected-sha256")
    command.add_argument("--format", choices=("text", "json"), default="text")


def dispatch(root, defaults, args):
    if args.onboard_action in {"status", "plan"}:
        return view(root, mode=args.onboard_action, provider=args.provider,
                    surface=args.surface, account_context=args.account_context,
                    credential_consumer=args.credential_consumer,
                    credential_class=args.credential_class, env_file=args.env_file)
    if args.onboard_action == "bridge":
        import agent_guide_bridge
        if not args.apply:
            if args.expected_sha256 is not None:
                raise ValueError("--expected-sha256 applies only to onboard bridge --apply")
            return agent_guide_bridge.bridge_status(Path(root))
        if not args.expected_sha256:
            raise ValueError("Preview bridge and supply its contentSha256 with --expected-sha256")
        return agent_guide_bridge.bridge_apply(Path(root), args.expected_sha256)
    raise ValueError("Unknown onboarding action")
