# Technical Notes

Notes incrementales pour preparer la fiche technique finale du projet.

## Objectif

Construire un workflow local avec NVIDIA NeMo Agent Toolkit (NAT), expose en API
via `nat serve`, puis utilisable depuis l'UI officielle NVIDIA NeMo Agent
Toolkit UI.

## Environnement

- Projet local : `/Users/mansour/Documents/projects/training_nvidia_nat`
- Python : 3.13.5 dans `.venv`
- NAT : `nvidia-nat==1.7.0`
- Node.js : `v25.9.0`
- npm : `11.12.1`

## Backend NAT

- Fichier workflow : `config.yml`
- Type de workflow : `chat_completion`
- LLM configure : NVIDIA NIM
- Modele : `meta/llama-3.1-70b-instruct`
- URL backend NVIDIA : `https://integrate.api.nvidia.com/v1`
- Variables attendues dans `.env` :
  - `NVIDIA_API_KEY`
  - `NVIDIA_BASE_URL`

Commande de validation :

```bash
nat validate --config_file config.yml
```

Commande serveur retenue :

```bash
nat serve --config_file config.yml --host 127.0.0.1 --port 8001
```

Pourquoi `8001` :

- Le port `8000` etait deja occupe par un processus Python local.
- NAT echouait avec `[Errno 48] address already in use`.
- `8001` a ete choisi comme port explicite et libre.

Endpoints utiles :

- Health : `GET http://127.0.0.1:8001/health`
- Swagger : `http://127.0.0.1:8001/docs`
- Chat completions : `POST http://127.0.0.1:8001/v1/chat/completions`

## Probleme SSL rencontre

Erreur :

```text
ssl.SSLCertVerificationError: certificate verify failed: unable to get local issuer certificate
```

Cause :

- Python 3.13 installe depuis python.org cherchait un fichier CA bundle dans :
  `/Library/Frameworks/Python.framework/Versions/3.13/etc/openssl/cert.pem`
- Le dossier OpenSSL existe, mais le certificat global n'etait pas installe.
- Les navigateurs ne sont pas touches car Chrome/Safari utilisent le Keychain
  macOS, pas forcement le meme chemin OpenSSL que Python.

Resolution propre recommandee :

```bash
"/Applications/Python 3.13/Install Certificates.command"
```

Note :

- Ne pas desactiver la verification SSL.
- `certifi` existe dans le `.venv`, mais l'objectif est de corriger Python
  proprement pour pouvoir lancer les commandes NAT standard.

## UI officielle NVIDIA

Decision :

- Ne pas recreer une UI custom.
- Ne pas creer de faux module `ui_manager`.
- Utiliser l'UI officielle NVIDIA.

Observation :

- Le snippet du cours :

```python
from ui_manager import ui_manager

ui_manager.start()
ui_manager.show_ui_link()
```

semble etre un helper fourni par l'environnement de formation, pas par le
package `nvidia-nat` installe localement.

Validation locale :

- `import ui_manager` echoue dans le `.venv`.
- L'extra `nvidia-nat[app]==1.7.0` installe `nvidia-nat-app`, mais ce package
  expose `nat_app`, qui correspond a Agent Performance Primitives, pas a l'UI
  web de chat.

Repo UI officiel clone :

```text
external/nat-ui
```

Source :

```text
https://github.com/NVIDIA/NeMo-Agent-Toolkit-UI.git
```

Installation realisee :

```bash
cd external/nat-ui
npm ci
```

Resultat :

- Installation OK.
- npm signale 14 vulnerabilites dans les dependances upstream.
- Aucun `npm audit fix` n'a ete lance pour ne pas modifier la lockfile
  officielle NVIDIA sans decision explicite.

Configuration UI a appliquer :

```text
NAT_BACKEND_URL=http://127.0.0.1:8001
PORT=3001
NEXT_INTERNAL_URL=http://localhost:3099
```

Configuration appliquee dans `external/nat-ui/.env` :

- `NAT_BACKEND_URL=http://127.0.0.1:8001`
- `PORT=3001`
- `NEXT_PUBLIC_NAT_WORKFLOW=Climate Assistant`
- `NEXT_PUBLIC_NAT_GREETING_TITLE="Climate Assistant"`
- `NEXT_PUBLIC_NAT_GREETING_SUBTITLE="Ask questions about climate, weather patterns, and temperature trends."`
- `NEXT_PUBLIC_NAT_INPUT_PLACEHOLDER="Ask a climate science question"`

Scripts projet ajoutes :

- `scripts/bootstrap_ui.sh`
- `scripts/serve_backend.sh`
- `scripts/serve_ui.sh`
- `scripts/validate_local.sh`

Principe :

- Le navigateur doit ouvrir le port proxy public (`PORT`, ici `3001`).
- Ne pas ouvrir directement le port interne Next.js `3099`.

## Validations deja faites

- `nat validate --config_file config.yml` : OK
- `python -m pytest` : OK
- `python -m ruff check .` : OK
- `GET /health` sur `http://127.0.0.1:8001` : OK quand le serveur est actif
- `npm ci` dans `external/nat-ui` : OK
- `bash -n scripts/serve_backend.sh` : OK
- `bash -n scripts/serve_ui.sh` : OK
- `bash -n scripts/bootstrap_ui.sh` : OK
- `bash -n scripts/validate_local.sh` : OK
- UI officielle lancee sur `http://localhost:3001` : OK
- Page UI `GET http://localhost:3001` : HTTP 200 OK
- Proxy UI vers NAT `POST http://localhost:3001/api/chat` : OK
- Test agent via proxy UI :
  - question : `What is climate change? Answer in one sentence.`
  - resultat : reponse climate assistant recue, donc UI proxy -> backend NAT -> NVIDIA NIM fonctionne.

## Limites upstream observees

`npm run typecheck` dans `external/nat-ui` echoue sur le repo UI officiel.
Les erreurs ne viennent pas de notre configuration locale, mais du code
TypeScript/tests upstream :

- types Jest non reconnus dans `__tests__`
- erreurs de typage React dans plusieurs composants
- incompatibilites de types dans certains tests utilitaires

Decision :

- Ne pas corriger ces erreurs dans le repo vendor NVIDIA pour l'instant.
- Ne pas lancer `npm audit fix` ni modifier la lockfile upstream sans besoin.
- Valider l'integration par demarrage du serveur UI et test HTTP/browser.

## Handoff sauvegarde

Un fichier `HANDOFF.md` a ete ajoute pour permettre a une autre personne ou un
autre agent de reprendre le projet. Il contient :

- objectif produit
- architecture NVIDIA/NAT/NIM/UI
- etat local valide
- points critiques
- strategie GitHub
- direction deploiement
- prochaines etapes

L'UI officielle NVIDIA reste volontairement hors Git via `external/`.
Elle est reconstruite localement avec `scripts/bootstrap_ui.sh`.

## Cleanup workshop NVIDIA

Dans le workshop, la fin de demo utilise :

```python
ui_manager.stop()
nat_process.terminate()
nat_process.wait()
print("Server stopped")
```

Interpretation :

- `ui_manager.stop()` arrete l'UI lancee par le helper de formation.
- `nat_process.terminate()` demande l'arret du serveur NAT lance en sous-processus.
- `nat_process.wait()` attend que le processus soit effectivement termine.

Equivalent local actuel :

- arreter `scripts/serve_backend.sh` avec `Ctrl+C`
- arreter `scripts/serve_ui.sh` avec `Ctrl+C`

Decision a integrer plus tard :

- ajouter `scripts/start_demo.sh` et `scripts/stop_demo.sh`
- stocker les PID dans `.tmp/`
- permettre un cycle demo propre :

```bash
scripts/start_demo.sh
scripts/stop_demo.sh
```

Objectif : avoir un cleanup fiable pour la demo portfolio, sans dependance au
helper `ui_manager` du workshop.
