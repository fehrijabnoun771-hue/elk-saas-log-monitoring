#!/usr/bin/env bash
cd "$(git rev-parse --show-toplevel)" || exit 1
G="\e[32m[OK]\e[0m"; R="\e[31m[ERREUR]\e[0m"; Y="\e[33m[A FAIRE]\e[0m"
ERR=0
ok()   { echo -e "$G $1"; }
ko()   { echo -e "$R $1"; ERR=$((ERR+1)); }
todo() { echo -e "$Y $1"; }
has()  { grep -qiF -- "$2" "$1" && ok "$2" || ko "$1 : section manquante -> $2"; }

D1=docs/01-analyse-fonctionnelle.md
D2=docs/02-kpi.md
D3=docs/03-architecture.md

echo "=== Fichiers ==="
for f in $D1 $D2 $D3; do
  if [ -s "$f" ]; then ok "$f ($(wc -l < "$f") lignes)"; else ko "$f absent ou vide"; fi
done

echo; echo "=== $D1 ==="
if [ -s $D1 ]; then
  for s in "## 1. Contexte" "## 2. Application SaaS monitorée" "## 3. Les 5 types de logs" \
           "## 4. Acteurs" "## 5. User stories" "## 6. Règles métier" "## 7. Diagramme"; do has $D1 "$s"; done
  n=$(grep -c "^- En tant qu" $D1)
  [ "$n" -ge 5 ] && ok "$n user stories" || ko "user stories : $n trouvées (minimum 5)"
  grep -q '^```mermaid' $D1 && ok "diagramme Mermaid présent" || ko "diagramme Mermaid absent"
fi

echo; echo "=== $D2 ==="
if [ -s $D2 ]; then
  n=$(grep -cE '^\| [1-5] \|' $D2)
  [ "$n" -eq 5 ] && ok "5 KPI dans le tableau" || ko "KPI : $n lignes trouvées (attendu 5)"
  has $D2 "3000"
  has $D2 "## Définitions"
fi

echo; echo "=== $D3 ==="
if [ -s $D3 ]; then
  for s in "## Schéma des conteneurs" "## Services Docker" "## Choix techniques" \
           "## Modèle Elasticsearch" "## MongoDB" "## Redis"; do has $D3 "$s"; done
  grep -q '^```mermaid' $D3 && ok "schéma Mermaid présent" || ko "schéma Mermaid absent"
  for svc in elasticsearch logstash kibana mongodb redis webapp; do
    grep -qi "$svc" $D3 || ko "service $svc non cité dans l'architecture"
  done
fi

echo; echo "=== Qualité Markdown ==="
for f in $D1 $D2 $D3; do
  [ -s "$f" ] || continue
  c=$(grep -c '^```' "$f")
  [ $((c % 2)) -eq 0 ] && ok "$f : blocs de code bien fermés" || ko "$f : bloc de code non fermé ($c balises)"
  grep -qn '^EOF$' "$f" && ko "$f : une ligne 'EOF' est restée dans le fichier"
done

echo; echo "=== A compléter par toi ==="
grep -n "à rédiger" $D1 $D2 $D3 2>/dev/null | while read -r l; do todo "$l"; done
grep -q "à rédiger" $D1 $D2 $D3 2>/dev/null || ok "aucun passage « à rédiger » restant"

echo; echo "=== Git ==="
git ls-files | grep -qx ".env" && ko ".env est suivi par Git (à retirer !)" || ok ".env non suivi par Git"
git status --short

echo
if [ $ERR -eq 0 ]; then
  echo -e "$G Tout est bon : tu peux faire commit et push."
else
  echo -e "$R $ERR erreur(s) : corrige avant de faire commit."
fi
exit $ERR
