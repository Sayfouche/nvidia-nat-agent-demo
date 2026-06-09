# training_nvidia_nat

Integration demo NVIDIA NeMo Agent Toolkit (NAT) + NVIDIA NIM + UI officielle
NVIDIA.

Ce repo montre comment assembler un workflow agentique NVIDIA de bout en bout :

```text
NVIDIA NIM -> NAT workflow -> NAT API backend -> official NVIDIA UI
```

## Demarrage

```bash
cd /Users/mansour/Documents/projects/training_nvidia_nat
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Cle API NVIDIA

Recupere une cle API NVIDIA Developer/NIM depuis `build.nvidia.com`, puis cree un
fichier `.env` local :

```bash
cp .env.example .env
```

Edite ensuite `.env` :

```bash
NVIDIA_API_KEY=ta_cle_api_nvidia
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
SSL_CERT_FILE=.venv/lib/python3.13/site-packages/certifi/cacert.pem
```

Ne commit jamais le fichier `.env`.

## Workflow NVIDIA NAT

Le workflow simple est dans `config.yml`. Il definit un LLM NVIDIA NIM
`meta/llama-3.1-70b-instruct` et un workflow `chat_completion` specialise sur
les questions de climat.

Pour valider la configuration :

```bash
nat validate --config_file config.yml
```

Pour lancer une question :

```bash
nat run --config_file config.yml --input "What is the greenhouse effect?"
```

Si tu obtiens une erreur SSL `CERTIFICATE_VERIFY_FAILED`, utilise le script de
lancement local :

```bash
scripts/run_climate_workflow.sh --input "What is the greenhouse effect?"
```

Le script active le `.venv`, charge `.env`, puis configure `SSL_CERT_FILE` avec
le bundle CA fourni par `certifi`.

## Workflow ReAct avec tools

Le workflow agentique est dans `configs/react_climate.yml`. Il expose cinq
tools Python locaux a NAT :

```text
list_countries
calculate_statistics
filter_by_country
find_extreme_years
create_visualization
```

Les tools sont declares dans `src/training_nvidia_nat/register.py` et les
fonctions testables dans `src/training_nvidia_nat/climate.py`.

Apres une modification du packaging NAT, reinstalle le package local :

```bash
python -m pip install -e . --no-build-isolation
```

Test rapide :

```bash
scripts/run_react_demo.sh "Compare the temperature trends of Canada and Brazil."
```

Backend ReAct pour l'UI :

```bash
scripts/serve_react_backend.sh
```

## Observability Phoenix

Phoenix est lance localement avec :

```bash
scripts/serve_phoenix.sh
```

La config `configs/react_climate_phoenix.yml` exporte les traces NAT vers :

```text
http://localhost:6006/v1/traces
```

Dans cet environnement NAT 1.7.0, il n'y a pas de composant tracing nomme
`phoenix`. Le branchement correct est donc :

```yaml
_type: otelcollector
endpoint: http://localhost:6006/v1/traces
```

Ordre de demo :

```bash
scripts/serve_phoenix.sh
NAT_CONFIG_FILE=configs/react_climate_phoenix.yml scripts/serve_react_backend.sh
scripts/serve_ui.sh
```

## UI officielle NVIDIA

L'UI officielle NVIDIA NeMo Agent Toolkit n'est pas versionnee dans ce repo.
Elle est recuperee comme dependance externe :

```bash
scripts/bootstrap_ui.sh
```

Elle sera installee dans :

```bash
external/nat-ui
```

Elle est configuree pour appeler le backend NAT local :

```text
http://127.0.0.1:8001
```

Terminal 1 - backend NAT :

```bash
scripts/serve_backend.sh
```

Terminal 2 - UI NVIDIA :

```bash
scripts/serve_ui.sh
```

Ouvre ensuite le port indique par le terminal UI. Par defaut :

```text
http://localhost:3001
```

Important : ne pas ouvrir directement `http://localhost:3099`. Ce port est le
serveur Next.js interne ; l'UI doit passer par le proxy public `3001`.

## Commandes utiles

```bash
python -m training_nvidia_nat
nat validate --config_file config.yml
nat validate --config_file configs/react_climate.yml
nat validate --config_file configs/react_climate_phoenix.yml
python -m pytest
python -m ruff check .
python -m black .
scripts/validate_local.sh
```

## Notes de reprise

Le contexte technique complet pour reprendre le projet est dans :

```bash
HANDOFF.md
TECHNICAL_NOTES.md
TECHNICAL_SHEET.md
```
