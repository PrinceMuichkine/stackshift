Directory structure:
└── cline-cline.git/
    ├── webview-ui/
    │   ├── scripts/
    │   │   └── build-react-no-split.js
    │   ├── .gitignore
    │   ├── public/
    │   │   ├── manifest.json
    │   │   ├── index.html
    │   │   └── robots.txt
    │   ├── package.json
    │   ├── tsconfig.json
    │   ├── package-lock.json
    │   └── src/
    │       ├── react-app-env.d.ts
    │       ├── App.tsx
    │       ├── reportWebVitals.ts
    │       ├── index.css
    │       ├── context/
    │       │   └── ExtensionStateContext.tsx
    │       ├── components/
    │       │   ├── history/
    │       │   │   ├── HistoryView.tsx
    │       │   │   └── HistoryPreview.tsx
    │       │   ├── settings/
    │       │   │   ├── SettingsView.tsx
    │       │   │   ├── TabNavbar.tsx
    │       │   │   ├── ApiOptions.tsx
    │       │   │   └── OpenRouterModelPicker.tsx
    │       │   ├── welcome/
    │       │   │   └── WelcomeView.tsx
    │       │   ├── mcp/
    │       │   │   ├── McpView.tsx
    │       │   │   ├── McpToolRow.tsx
    │       │   │   └── McpResourceRow.tsx
    │       │   ├── chat/
    │       │   │   ├── TaskHeader.tsx
    │       │   │   ├── ChatTextArea.tsx
    │       │   │   ├── ChatView.tsx
    │       │   │   ├── BrowserSessionRow.tsx
    │       │   │   ├── ChatRow.tsx
    │       │   │   ├── Announcement.tsx
    │       │   │   ├── AutoApproveMenu.tsx
    │       │   │   └── ContextMenu.tsx
    │       │   └── common/
    │       │       ├── CodeBlock.tsx
    │       │       ├── VSCodeButtonLink.tsx
    │       │       ├── CodeAccordian.tsx
    │       │       ├── Thumbnails.tsx
    │       │       ├── Demo.tsx
    │       │       └── MarkdownBlock.tsx
    │       ├── setupTests.ts
    │       ├── utils/
    │       │   ├── context-mentions.ts
    │       │   ├── mcp.ts
    │       │   ├── textMateToHljs.ts
    │       │   ├── getLanguageFromPath.ts
    │       │   ├── validate.ts
    │       │   ├── vscode.ts
    │       │   └── format.ts
    │       └── index.tsx
    ├── .vscode-test.mjs
    ├── .prettierignore
    ├── tsconfig.test.json
    ├── CHANGELOG.md
    ├── .github/
    │   ├── dependabot.yml
    │   ├── workflows/
    │   │   └── test.yml
    │   ├── pull_request_template.md
    │   └── ISSUE_TEMPLATE/
    │       ├── config.yml
    │       └── bug_report.yml
    ├── .eslintrc.json
    ├── assets/
    │   ├── docs/
    │   └── icons/
    ├── package.json
    ├── .nvmrc
    ├── .prettierrc.json
    ├── CODE_OF_CONDUCT.md
    ├── esbuild.js
    ├── LICENSE
    ├── tsconfig.json
    ├── README.md
    ├── .vscodeignore
    ├── CONTRIBUTING.md
    └── src/
        ├── api/
        │   ├── transform/
        │   │   ├── stream.ts
        │   │   ├── openai-format.ts
        │   │   ├── o1-format.ts
        │   │   └── gemini-format.ts
        │   ├── providers/
        │   │   ├── openai.ts
        │   │   ├── anthropic.ts
        │   │   ├── bedrock.ts
        │   │   ├── lmstudio.ts
        │   │   ├── openai-native.ts
        │   │   ├── ollama.ts
        │   │   ├── vertex.ts
        │   │   ├── openrouter.ts
        │   │   └── gemini.ts
        │   └── index.ts
        ├── services/
        │   ├── glob/
        │   │   └── list-files.ts
        │   ├── tree-sitter/
        │   │   ├── queries/
        │   │   │   ├── c.ts
        │   │   │   ├── c-sharp.ts
        │   │   │   ├── go.ts
        │   │   │   ├── php.ts
        │   │   │   ├── cpp.ts
        │   │   │   ├── javascript.ts
        │   │   │   ├── index.ts
        │   │   │   ├── typescript.ts
        │   │   │   ├── rust.ts
        │   │   │   ├── swift.ts
        │   │   │   ├── python.ts
        │   │   │   ├── java.ts
        │   │   │   └── ruby.ts
        │   │   ├── index.ts
        │   │   └── languageParser.ts
        │   ├── ripgrep/
        │   │   └── index.ts
        │   ├── browser/
        │   │   ├── UrlContentFetcher.ts
        │   │   └── BrowserSession.ts
        │   └── mcp/
        │       └── McpHub.ts
        ├── test/
        │   └── extension.test.ts
        ├── core/
        │   ├── Cline.ts
        │   ├── mentions/
        │   │   └── index.ts
        │   ├── prompts/
        │   │   ├── responses.ts
        │   │   └── system.ts
        │   ├── assistant-message/
        │   │   ├── parse-assistant-message.ts
        │   │   ├── diff.ts
        │   │   └── index.ts
        │   ├── webview/
        │   │   ├── ClineProvider.ts
        │   │   ├── getNonce.ts
        │   │   └── getUri.ts
        │   └── sliding-window/
        │       └── index.ts
        ├── extension.ts
        ├── shared/
        │   ├── array.ts
        │   ├── HistoryItem.ts
        │   ├── context-mentions.ts
        │   ├── mcp.ts
        │   ├── WebviewMessage.ts
        │   ├── getApiMetrics.ts
        │   ├── array.test.ts
        │   ├── combineApiRequests.ts
        │   ├── combineCommandSequences.ts
        │   ├── api.ts
        │   ├── ExtensionMessage.ts
        │   └── AutoApprovalSettings.ts
        ├── integrations/
        │   ├── terminal/
        │   │   ├── TerminalProcess.ts
        │   │   ├── TerminalRegistry.ts
        │   │   └── TerminalManager.ts
        │   ├── notifications/
        │   │   └── index.ts
        │   ├── diagnostics/
        │   │   ├── DiagnosticsMonitor.ts
        │   │   └── index.ts
        │   ├── theme/
        │   │   ├── getTheme.ts
        │   │   └── default-themes/
        │   │       ├── dark_plus.json
        │   │       ├── dark_vs.json
        │   │       ├── light_plus.json
        │   │       ├── hc_black.json
        │   │       ├── light_modern.json
        │   │       ├── dark_modern.json
        │   │       ├── hc_light.json
        │   │       └── light_vs.json
        │   ├── workspace/
        │   │   ├── WorkspaceTracker.ts
        │   │   └── get-python-env.ts
        │   ├── editor/
        │   │   ├── DecorationController.ts
        │   │   ├── DiffViewProvider.ts
        │   │   └── detect-omission.ts
        │   └── misc/
        │       ├── process-images.ts
        │       ├── export-markdown.ts
        │       ├── open-file.ts
        │       └── extract-text.ts
        ├── exports/
        │   ├── index.ts
        │   ├── cline.d.ts
        │   └── README.md
        └── utils/
            ├── path.test.ts
            ├── path.ts
            ├── cost.ts
            ├── fs.test.ts
            ├── cost.test.ts
            ├── fs.ts
            └── string.ts
