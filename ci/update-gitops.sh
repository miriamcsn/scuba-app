#!/bin/sh
# Atualiza as tags das imagens no repositório GitOps e faz push.
# Usado pelo Jenkins e pelo Azure DevOps, depois que as duas imagens já estão no Harbor.
#
# Uso:  sh ci/update-gitops.sh <tag>
# Variáveis:
#   GITOPS_URL   URL https do repositório GitOps, já com credencial (obrigatória)
#   VALUES_FILE  arquivo de valores do ambiente (padrão: envs/demo/values.yaml)
#   CI_NAME      nome do autor do commit (padrão: ci)
set -eu

TAG="${1:?informe a tag das imagens}"
VALUES_FILE="${VALUES_FILE:-envs/demo/values.yaml}"
WORKDIR="$(mktemp -d)"

git clone --quiet "$GITOPS_URL" "$WORKDIR"
cd "$WORKDIR"

# As linhas de tag são marcadas com os comentários "# backend-tag" e "# frontend-tag".
for comp in backend frontend; do
  sed -i -E "s|^([[:space:]]*tag:).*# ${comp}-tag[[:space:]]*$|\1 \"${TAG}\" # ${comp}-tag|" "$VALUES_FILE"
  if ! grep -q "\"${TAG}\" # ${comp}-tag" "$VALUES_FILE"; then
    echo "ERRO: linha marcada com '# ${comp}-tag' não encontrada em ${VALUES_FILE}" >&2
    exit 1
  fi
done

git config user.email "ci@scuba.demo"
git config user.name "${CI_NAME:-ci}"
git add "$VALUES_FILE"

if git diff --cached --quiet; then
  echo "As tags já estão em ${TAG}; nada a fazer."
  exit 0
fi

git commit --quiet -m "deploy: scuba ${TAG}"
git push --quiet origin HEAD
echo "Tags atualizadas para ${TAG} em ${VALUES_FILE}."
