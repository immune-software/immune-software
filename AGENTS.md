# AGENTS.md

**One line.** `README.md` holds the Immune software manifesto, `PROOF_OF_SECURITY.md` its first tool, `EXAMPLE.md` the hello world, `targets/` and `BOARD.md` the board; the tooling is four agent skills in `.github/skills/`.

## Rules

1. **Keys are money.** Never print, store, ask for or move a private key. Funding, publishing, merging and pull requests are human steps.
2. **Throwaway keys only in tests.** Never fund them; remove test images and test manifests afterwards.
3. **One source.** The skill files are the source. `EXAMPLE.md`, `board.sh` and `.github/workflows/board.yml` hold copies; the check below compares them.
4. **Self-contained skills.** Links stay inside the skill folder; no `../`.
5. **Frontmatter:** `name` (= folder), `description` (what, then "Use when…", ≤ 1024 chars), `metadata.version`; bump the version on change.
6. **Progressive.** `SKILL.md` ≤ 500 lines; code in `scripts/` (executable) or `assets/`, long tables in `references/`.
7. **Terse.** Tables over prose, copy-paste-ready commands, plain headers. `README.md` stays short: the principles and the tools. `PROOF_OF_SECURITY.md` stays short: the idea, the board, the invitation. Walkthroughs go to `EXAMPLE.md`, procedures to the skills.
8. **Generated board.** `BOARD.md` comes from `board.sh`: never edit it by hand. A target enters `targets/` by pull request, after the run-board review.

## Check

Prints nothing when everything passes:

```bash
for f in .github/skills/*/SKILL.md; do
  d=$(dirname "$f"); n=$(basename "$d")
  grep -q "^name: $n$" "$f" || echo "FAIL name != folder: $f"
  desc=$(grep -m1 '^description:' "$f"); [ ${#desc} -le 1039 ] || echo "FAIL description > 1024: $f"
  [ "$(wc -l < "$f")" -le 500 ] || echo "FAIL > 500 lines: $f"
  grep -nE '\]\((\.\./|/|~)' "$f" "$d"/*/*.md 2>/dev/null && echo "FAIL link leaves skill: $n"
  for s in "$d"/scripts/*.sh; do [ -e "$s" ] || continue; bash -n "$s" || echo "FAIL syntax: $s"; [ -x "$s" ] || echo "FAIL not executable: $s"; done
  for s in "$d"/scripts/*.py; do [ -e "$s" ] || continue; python3 -c 'import ast, sys; ast.parse(open(sys.argv[1]).read())' "$s" || echo "FAIL syntax: $s"; done
done
for p in seal-target/assets/seal.sh seal-target/assets/Dockerfile run-board/scripts/board.sh run-board/assets/board.yml; do
  python3 -c 'import sys; sys.exit(open(sys.argv[1]).read() not in open("EXAMPLE.md").read())' ".github/skills/$p" || echo "FAIL EXAMPLE.md differs from $p"
done
cmp -s .github/skills/run-board/scripts/board.sh board.sh || echo "FAIL board.sh differs from the skill"
cmp -s .github/skills/run-board/assets/board.yml .github/workflows/board.yml || echo "FAIL board.yml differs from the skill"
grep -oE '\]\([^)#:]+[)#]' README.md PROOF_OF_SECURITY.md EXAMPLE.md | while IFS=: read -r f l; do l=${l#*(}; [ -e "${l%?}" ] || echo "FAIL dead link in $f: ${l%?}"; done
```
