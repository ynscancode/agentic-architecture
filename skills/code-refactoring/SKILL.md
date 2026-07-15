---
name: code-refactoring
description: Use when cleaning up existing code without changing behavior — removing dead code/duplication, tightening overly verbose implementations, and keeping file/folder structure and import pathways consistent across frontend and backend. Primary skill for the code-refactoring-engineer subagent.
---

# Code Refactoring

Refactoring changes structure, not behavior. Every pass must end with the app behaving identically to before — if a "cleanup" changes output, it's a bug fix or feature change, not a refactor, and should be flagged as such instead of silently bundled in.

## Workflow

1. **Baseline first.** Before touching anything, know what currently passes: run the existing test suite / smoke test / build / lint if one exists, and note the result. This is what you diff against after.
2. **Identify targets**, in priority order:
   - Dead code: unused exports, functions, variables, files no longer imported anywhere
   - Duplication: near-identical logic copy-pasted across files that should be a shared function/module
   - Over-abstraction: unnecessary indirection, wrapper functions/classes that don't earn their complexity
   - Inconsistent patterns: same kind of problem solved differently in different files (e.g., two different error-handling styles)
   - File/folder structure drift: files in the wrong directory relative to the project's established structure, inconsistent naming conventions, import paths that reach across layers they shouldn't (e.g., a route file reaching past the service layer directly into the DB)
3. **Cross-stack consistency check.** For projects with parallel frontend/backend definitions (shared constants, enums, category lists, API contracts mirrored on both sides), verify both sides actually match — this is a common drift point. Don't assume they're in sync; grep both and compare.
4. **Make the smallest change that achieves the cleanup.** Don't restructure beyond what's needed to remove the actual problem found in step 2.
5. **Re-run the baseline.** Tests/build/lint must produce the same passing result as step 1. If behavior changed, you introduced a bug — fix it or revert that piece.
6. **Report concretely**: what was removed/consolidated/moved, why, and confirmation the baseline still holds.

## File pathway cleanliness checklist
- [ ] No unused imports or dead files left behind
- [ ] No file importing across a layer boundary the project doesn't otherwise allow (check existing architecture — e.g., routes → services → db, not routes → db directly)
- [ ] Naming and directory placement consistent with sibling files of the same kind
- [ ] Shared constants/types that exist on both frontend and backend are actually identical, not just similarly named
- [ ] No circular imports introduced

## Anti-patterns
- Don't refactor and add a feature in the same pass — keep them separable so a regression is easy to bisect.
- Don't delete code just because it looks unused without confirming via grep across the whole codebase (including dynamic imports/string-based references).
- Don't introduce a new abstraction "for consistency" if it adds more code than it removes without a concrete duplication problem to justify it.
