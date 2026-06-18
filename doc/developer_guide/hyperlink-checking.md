# Check for Broken Hyperlinks

AI Lab's GitHub workflow [hyperlinks.yaml](https://github.com/exasol/ai-lab/blob/main/.github/workflows/hyperlinks.yaml) checks the validity of hyperlinks in Markdown documentation.

If a specific link temporarily is unreachable, you can ignore it as specified by the following table.

| Files | Tool | How to ignore broken links? |
|-------|------|-----------------------------|
| Markdown files, e.g. README or Changelog | GitHub action [lycheeverse/lychee-action](https://github.com/lycheeverse/lychee-action) | Add regexp to file `.lycheeignore` |
