import katex from 'katex'

/**
 * 将文本中的行内公式 $...$ 和块级公式 $$...$$ 渲染为HTML
 */
export function renderFormulas(html) {
  // 块级公式 $$...$$
  html = html.replace(/\$\$([\s\S]+?)\$\$/g, (_, formula) => {
    try {
      return katex.renderToString(formula.trim(), { displayMode: true, throwOnError: false })
    } catch {
      return `$$${formula}$$`
    }
  })
  // 行内公式 $...$
  html = html.replace(/\$([^\$\n]+?)\$/g, (_, formula) => {
    try {
      return katex.renderToString(formula.trim(), { displayMode: false, throwOnError: false })
    } catch {
      return `$${formula}$`
    }
  })
  return html
}

export default katex
