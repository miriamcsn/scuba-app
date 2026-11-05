# scuba-app — Scuba Dive Log (código do app)

App de registro de mergulhos usado na demo de CI/CD no NKP: backend em Python (FastAPI),
banco MySQL e frontend em HTML/JS servido por nginx sem root.

Este repositório tem só o código e os Dockerfiles. O deploy fica no repositório GitOps
[`scuba-gitops`](https://github.com/miriamcsn/scuba-gitops), que o Flux e o Argo CD observam.
O CI nunca faz deploy direto: ele publica as imagens no Harbor e grava as novas tags no
repositório GitOps.

## Estrutura

```
backend/          FastAPI + testes (pytest) + Dockerfile multi-stage
  tests/          testes da API, rodam com SQLite (sem MySQL)
frontend/         index.html + nginx.conf + Dockerfile (nginx sem root, porta 8080)
ci/
  update-gitops.sh  grava as novas tags no repositório GitOps (usado pelos dois CIs)
compose.yml       ambiente local com Docker ou Podman Compose
Jenkinsfile       CI com Jenkins no NKP
azure-pipelines.yml  CI com Azure DevOps (agente self-hosted no NKP)
```

## Rodar localmente

```bash
docker compose up --build      # ou: podman compose up --build
# abra http://localhost:8080
```

O build do backend já roda os testes. Para rodar só os testes:

```bash
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q tests
```

## O que o CI faz

1. **Segredos:** Gitleaks procura tokens e senhas no código. Se achar, o pipeline para.
2. **Backend:** o kaniko constrói o Dockerfile dentro do cluster, sem Docker. A etapa
   `tests` do Dockerfile roda o pytest; se um teste falhar, nenhuma imagem é gerada.
3. **Frontend:** o kaniko constrói e publica a imagem do nginx.
4. **Tags:** `ci/update-gitops.sh` grava a tag (7 primeiros caracteres do commit) em
   `envs/demo/values.yaml` no repositório GitOps. O Flux ou o Argo CD aplica a mudança.

As imagens vão para `<HARBOR_HOST>/scuba/scuba-backend` e `<HARBOR_HOST>/scuba/scuba-frontend`.

## Antes do primeiro uso

Troque `<HARBOR_HOST>` pelo endereço do Harbor do NKP:

```bash
grep -rn "<HARBOR_HOST>" .
```

No Harbor, crie o projeto `scuba` e uma robot account com permissão de push nele.

## Cenas da demo

- **Segredo commitado:** crie um arquivo `config.txt` com uma linha `api_key = "..."`,
  trocando os pontos por 32 caracteres hexadecimais aleatórios, e faça push. O Gitleaks
  barra o build. Depois apague o arquivo e faça push de novo. (A chave não aparece aqui
  de propósito: se estivesse neste README, o Gitleaks barraria todos os builds.)
- **Teste falhando:** mude o texto `"Scuba Dive Log"` na rota `/` de `backend/app/main.py`
  e faça push. A etapa de testes falha e nenhuma imagem é publicada.
- **Do commit ao app no ar:** mude um texto do `frontend/index.html` e faça push.

Credenciais do `compose.yml` são apenas de demo.
