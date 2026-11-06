#!/usr/bin/env bash
cd "$(git rev-parse --show-toplevel)" || exit 1
REPO="fehrijabnoun771-hue/elk-saas-log-monitoring"
G="\e[32m[OK]\e[0m"; R="\e[31m[ERREUR]\e[0m"; ERR=0
ok() { echo -e "$G $1"; }
ko() { echo -e "$R $1"; ERR=$((ERR+1)); }

git fetch -q 2>/dev/null

echo "=== 1. Dépôt GitHub ==="
vis=$(gh repo view $REPO --json visibility --jq '.visibility' 2>/dev/null)
[ "$vis" = "PUBLIC" ] && ok "dépôt public" || ko "dépôt non public ($vis)"
code=$(curl -s -o /dev/null -w "%{http_code}" https://github.com/$REPO)
[ "$code" = "200" ] && ok "lien accessible sans connexion (200)" || ko "lien inaccessible (code $code)"

echo; echo "=== 2. Structure du projet ==="
for d in docs/img webapp/app/models webapp/app/routes webapp/app/templates webapp/app/static \
         logstash/pipeline elasticsearch kibana/exports scripts tests data/logs; do
  [ -d "$d" ] && ok "$d" || ko "dossier manquant : $d"
done
for f in README.md .gitignore .env.example docker-compose.yml; do
  [ -f "$f" ] && ok "$f" || ko "fichier manquant : $f"
done

echo; echo "=== 3. Documents ==="
./scripts/verif-docs.sh >/dev/null 2>&1 && ok "documents 01, 02, 03 conformes" || ko "documents non conformes (lance ./scripts/verif-docs.sh)"
[ -s docs/sprint-0-bilan.md ] && ok "docs/sprint-0-bilan.md présent" || ko "bilan absent"
if grep -rq "à compléter\|à rédiger" docs/; then ko "il reste des passages à compléter :"; grep -rn "à compléter\|à rédiger" docs/; else ok "aucun passage à compléter"; fi

echo; echo "=== 4. Backlog ==="
total=$(gh issue list --state all --limit 50 --json number --jq 'length')
[ "$total" = "12" ] && ok "12 issues créées" || ko "issues : $total (attendu 12)"
for n in 1 2; do
  st=$(gh issue view $n --json state --jq '.state' 2>/dev/null)
  [ "$st" = "CLOSED" ] && ok "issue #$n fermée" || ko "issue #$n pas fermée ($st)"
done
op=$(gh issue list --state open --json number --jq 'length')
[ "$op" = "10" ] && ok "10 issues ouvertes (#3 à #12)" || ko "issues ouvertes : $op (attendu 10)"
for pair in S0:2 S1:3 S2:2 S3:3 S4:2; do
  l=${pair%%:*}; n=${pair##*:}
  c=$(gh issue list --state all --label $l --json number --jq 'length')
  [ "$c" = "$n" ] && ok "label $l : $c issues" || ko "label $l : $c (attendu $n)"
done

echo; echo "=== 5. Git : branches et tag ==="
m=$(git rev-parse main); d=$(git rev-parse develop)
om=$(git rev-parse origin/main); od=$(git rev-parse origin/develop)
[ "$m" = "$d" ] && [ "$m" = "$om" ] && [ "$m" = "$od" ] && ok "main, develop, origin/main et origin/develop synchronisés" || ko "branches non synchronisées"
tag=$(git rev-parse "v0.0-sprint0^{commit}" 2>/dev/null)
[ "$tag" = "$m" ] && ok "tag v0.0-sprint0 sur le dernier commit de main" || ko "tag v0.0-sprint0 absent ou pas sur le dernier commit"
remote_tag=$(git ls-remote --tags origin v0.0-sprint0 | wc -l)
[ "$remote_tag" -ge 1 ] && ok "tag poussé sur GitHub" || ko "tag non poussé"
[ -z "$(git status --short)" ] && ok "copie de travail propre" || { ko "modifications non commitées :"; git status --short; }

echo; echo "=== 6. Sécurité ==="
git ls-files | grep -qx ".env" && ko ".env est suivi par Git" || ok ".env non suivi par Git"
PAT="pass""word|sec""ret|tok""en"
if git log --all -p | grep -iE "$PAT" | grep -qvi "changeme"; then ko "mot sensible trouvé dans l'historique"; else ok "aucun secret dans l'historique"; fi

echo
if [ $ERR -eq 0 ]; then
  echo -e "$G SPRINT 0 TERMINÉ. Lien à partager : https://github.com/$REPO"
else
  echo -e "$R $ERR problème(s) à corriger avant de clore le Sprint 0."
fi
exit $ERR
