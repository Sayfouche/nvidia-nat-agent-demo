# training_nvidia_nat

Projet Python local avec environnement virtuel dedie.

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
```
