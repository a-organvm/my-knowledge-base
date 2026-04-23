// Package main implements a plan file generator for the knowledge base.
//
// Generates dated plan files from templates, ensuring proper naming
// conventions and versioning per the plan file discipline.
//
// Usage:
//
//	go run scripts/planner_generator.go --slug "my-plan-name" --dir .claude/plans/
//	go run scripts/planner_generator.go --slug "refactor-pipeline" --template plan.tmpl
package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"text/template"
	"time"
)

// PlanData holds the template variables for plan generation.
type PlanData struct {
	Date        string
	Slug        string
	Title       string
	Version     int
	GeneratedAt string
	Directory   string
}

const defaultTemplate = `# Plan: {{.Title}}

**Date:** {{.Date}}
**Slug:** {{.Slug}}
**Version:** v{{.Version}}
**Generated:** {{.GeneratedAt}}

## Objective

<!-- What is the goal of this plan? -->

## Context

<!-- What is the current state? What triggered this plan? -->

## Approach

<!-- How will we achieve the objective? -->

### Phase 1: Discovery

- [ ] Identify existing state
- [ ] Map dependencies
- [ ] Document constraints

### Phase 2: Implementation

- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

### Phase 3: Verification

- [ ] Validate changes
- [ ] Run tests
- [ ] Review with stakeholder

## Success Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| | | | |

## Notes

<!-- Additional context, references, links -->
`

func slugToTitle(slug string) string {
	words := strings.Split(slug, "-")
	for i, w := range words {
		if len(w) > 0 {
			words[i] = strings.ToUpper(w[:1]) + w[1:]
		}
	}
	return strings.Join(words, " ")
}

func findNextVersion(dir, date, slug string) int {
	version := 1
	base := fmt.Sprintf("%s-%s", date, slug)

	// Check if base file exists
	if _, err := os.Stat(filepath.Join(dir, base+".md")); err == nil {
		version = 2
	}

	// Check versioned files
	for {
		name := fmt.Sprintf("%s-v%d.md", base, version)
		if _, err := os.Stat(filepath.Join(dir, name)); os.IsNotExist(err) {
			break
		}
		version++
	}

	return version
}

func main() {
	slug := flag.String("slug", "", "Plan slug (required, e.g., 'refactor-pipeline')")
	dir := flag.String("dir", ".claude/plans", "Output directory for plan files")
	tmplFile := flag.String("template", "", "Custom template file (optional)")
	flag.Parse()

	if *slug == "" {
		fmt.Fprintln(os.Stderr, "Error: --slug is required")
		fmt.Fprintln(os.Stderr, "Usage: planner_generator --slug <slug> [--dir <dir>] [--template <file>]")
		os.Exit(1)
	}

	now := time.Now().UTC()
	date := now.Format("2006-01-02")

	// Ensure output directory exists
	if err := os.MkdirAll(*dir, 0o755); err != nil {
		fmt.Fprintf(os.Stderr, "Error creating directory %s: %v\n", *dir, err)
		os.Exit(1)
	}

	// Determine version (never overwrite)
	version := findNextVersion(*dir, date, *slug)

	data := PlanData{
		Date:        date,
		Slug:        *slug,
		Title:       slugToTitle(*slug),
		Version:     version,
		GeneratedAt: now.Format(time.RFC3339),
		Directory:   *dir,
	}

	// Build filename
	var filename string
	if version == 1 {
		filename = fmt.Sprintf("%s-%s.md", date, *slug)
	} else {
		filename = fmt.Sprintf("%s-%s-v%d.md", date, *slug, version)
	}
	outPath := filepath.Join(*dir, filename)

	// Parse template
	var tmpl *template.Template
	var err error

	if *tmplFile != "" {
		tmpl, err = template.ParseFiles(*tmplFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error parsing template %s: %v\n", *tmplFile, err)
			os.Exit(1)
		}
	} else {
		tmpl, err = template.New("plan").Parse(defaultTemplate)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error parsing default template: %v\n", err)
			os.Exit(1)
		}
	}

	// Write output
	f, err := os.Create(outPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error creating file %s: %v\n", outPath, err)
		os.Exit(1)
	}
	defer f.Close()

	if err := tmpl.Execute(f, data); err != nil {
		fmt.Fprintf(os.Stderr, "Error rendering template: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Created: %s\n", outPath)
}
