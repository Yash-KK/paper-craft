export function prepareMarkdownContent(content: string): string {
  return content
    .replace(
      /\\\[([\s\S]*?)\\\]/g,
      (_m, tex: string) => `\n$$\n${tex.trim()}\n$$\n`
    )
    .replace(/\\\(([\s\S]*?)\\\)/g, (_m, tex: string) => `$${tex}$`)
}
