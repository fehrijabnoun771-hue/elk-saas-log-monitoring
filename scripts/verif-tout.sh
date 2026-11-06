#!/usr/bin/env bash
G="\e[32mOK\e[0m"; R="\e[31mMANQUANT\e[0m"; Y="\e[33m--\e[0m"
cmd()  { command -v "$2" >/dev/null 2>&1 && echo -e "[$G] $1 : $($3 2>&1 | head -1 | cut -c1-70)" || echo -e "[$R] $1"; }
pkg()  { v=$(dpkg-query -W -f='${Version}' "$1" 2>/dev/null) && echo -e "[$G] $1 (natif) : $v" || echo -e "[$Y] $1 non installé en natif (ira dans Docker)"; }
img()  { i=$(docker images --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | grep -i "$1" | head -1); [ -n "$i" ] && echo -e "[$G] image $1 : $i" || echo -e "[$Y] image $1 pas encore téléchargée (Sprint 1)"; }

echo "=== Outils ==="
cmd "Git" git "git --version"
cmd "curl" curl "curl --version"
cmd "Python" python3 "python3 --version"
cmd "pip" pip3 "pip3 --version"
python3 -m venv --help >/dev/null 2>&1 && echo -e "[$G] python3-venv" || echo -e "[$R] python3-venv"
cmd "GitHub CLI" gh "gh --version"
cmd "Docker" docker "docker --version"
docker compose version >/dev/null 2>&1 && echo -e "[$G] Docker Compose : $(docker compose version)" || echo -e "[$R] Docker Compose"
docker info >/dev/null 2>&1 && echo -e "[$G] Docker sans sudo" || echo -e "[$R] Docker sans sudo / démon arrêté"

echo; echo "=== Stack ELK installée en natif (test) ==="
pkg elasticsearch; pkg logstash; pkg kibana
for s in elasticsearch logstash kibana; do echo "   service $s : $(systemctl is-active $s 2>/dev/null)"; done
echo -n "   Elasticsearch répond ? "; curl -s -m 3 http://localhost:9200 | grep -o '"number" : "[^"]*"' || echo "non (arrêté)"

echo; echo "=== Images Docker du projet ==="
for i in elasticsearch logstash kibana mongo redis python; do img $i; done

echo; echo "=== Ports du projet ==="
for p in 9200 5601 5044 27017 6379 8000; do ss -tln | grep -q ":$p " && echo -e "[\e[33mOCCUPÉ\e[0m] $p" || echo -e "[$G] $p libre"; done

echo; echo "=== Système ==="
echo "Ubuntu : $(lsb_release -ds)  |  RAM : $(free -h | awk '/Mem/{print $2" ("$7" dispo)"}')  |  Disque : $(df -h / | awk 'NR==2{print $4}') libres  |  CPU : $(nproc)"
[ "$(sysctl -n vm.max_map_count)" -ge 262144 ] && echo -e "[$G] vm.max_map_count = $(sysctl -n vm.max_map_count)" || echo -e "[\e[33mA CORRIGER\e[0m] vm.max_map_count"
