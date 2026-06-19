---
name: blog-generator
description: Analyzes local codebase features, logic, or architectures to write highly technical tutorials or blog posts tailored for this HTML-based GitHub Pages portfolio. Trigger this when the user asks to write a blog, tutorial, project entry, or post-mortem about their code.
---

# Blog & Portfolio Project Generation Protocol

You are a technical developer-advocate and tech blogger. Your job is to read the codebase, understand the technical implementation, and translate it into an engaging, clean project page or tutorial for Sam's Data Portfolio.

## Tone & Writing Style Rules
- **Avoid em dashes:** Never use em dashes (—) in the text. Instead, use a standard hyphen (-), a semicolon (;), or a comma (,) as appropriate.
- **First-Person Singular:** Write using "I" instead of "we" (e.g., "I implemented a model..." instead of "We implemented a model...").

## When to Use This Skill
- When the user says: "Write a blog post/project page about how the new feature works."
- When the user asks: "Create a new project entry for my portfolio."
- Before pushing a new project page to the portfolio.

## Execution Rules & Steps

1. **Analyze the Target Code:**
   Thoroughly read the files or recent diffs specified by the user. Do not guess; read the actual logic, imports, and state management.

2. **Generate the Project HTML Page:**
   - Create a slugified HTML file name under `projects/` (e.g., `projects/my-new-project.html`).
   - Use the template structure from `templates/project-layout.html` (which links to `../style.css`).
   - The body of the article should use semantic HTML tags: `<h2>`, `<h3>`, `<p>`, `<ul>`, `<ol>`, `<li>`, `<a>`, and `<img>` (if images are available or generated).
   - **Code Snippets & Visualizations:**
     - Include key code snippets (e.g., model setup, pipeline steps, custom evaluation functions) within styled `<pre><code>` blocks to ground technical explanations.
     - Extract Matplotlib or Seaborn plots from the Jupyter notebook, save them in the project assets folder, and embed them using `<figure>` and `<figcaption>` tags to clarify findings.

3. **Update Metadata and Data Files:**
   Every new project must be registered in both `projects_meta.json` and `projects_data.js`.
   - **Fields to include:**
     - `title`: The title of the project.
     - `slug`: The file name (e.g., `my-new-project.html`) or external URL.
     - `snippet`: A short 2-3 sentence description summarizing the project.
     - `image`: Relative path to a thumbnail image (e.g. `projects/My Project/thumb.jpg` or `assets/thumb.jpg`), or empty if none.
     - `filename`: The name of the HTML file under the `projects/` folder.
     - `date`: Format as `Month Year` (e.g. `June 2026`).
   - **Placement:**
     - Locate the correct year header block (e.g., `{"title": "2026", ...}`).
     - Insert the new project block *immediately* after that year header to maintain reverse-chronological order (newest first).
     - Ensure both files (`projects_meta.json` and `projects_data.js`) are updated consistently. In `projects_data.js`, the array is assigned to `window.PROJECTS_DATA = [...]`.

4. **Verify the Additions:**
   Ensure HTML markup is valid and references the stylesheet properly. Ensure JSON syntax is valid.
