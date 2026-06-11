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

## Lesson - NAT tool registration

La lecon introduit le passage du workflow simple `chat_completion` a un agent
ReAct outille.

Objectif conceptuel :

```text
Python function -> NAT tool -> ReAct agent -> tool call -> observation -> final answer
```

Flow de registration d'un tool NAT :

```text
1. Input Schema -> 2. Config Class -> 3. Wrapper Function -> 4. YAML Config
```

### Step 1 - Input Schema

Le schema d'entree definit les parametres exposables au LLM quand il appelle le
tool. Exemple du workshop :

```python
from pydantic import BaseModel, Field


class CalculateStatsInput(BaseModel):
    country: str = Field(
        default="",
        description=(
            "Country name to filter by (e.g., 'United States', 'France'). "
            "Leave empty for global statistics."
        ),
    )
```

Points importants :

- utiliser Pydantic `BaseModel`
- documenter chaque champ avec `Field(description=...)`
- la description sert au LLM pour savoir quand et comment appeler le tool
- `default=""` permet de representer le cas global sans pays filtre

Decision probable pour notre repo :

- creer plus tard des schemas dans `src/training_nvidia_nat/tools/`
- tester les fonctions metier independamment du LLM
- garder `config.yml` comme baseline simple
- ajouter un workflow separe pour ReAct/tools, par exemple
  `configs/react_climate.yml`

### Step 2 - Config Class

La classe de config enregistre le tool dans NAT avec un nom stable. Exemple du
workshop :

```python
from nat.data_models.function import FunctionBaseConfig


class CalculateStatisticsConfig(
    FunctionBaseConfig,
    name="simple_calculate_statistics",
):
    """Configuration for calculating climate statistics."""

    pass
```

Points importants :

- heriter de `FunctionBaseConfig`
- passer `name="simple_calculate_statistics"` dans la declaration de classe
- ce nom devient l'identifiant NAT du tool
- le YAML pourra ensuite referencer ce tool avec :

```yaml
functions:
  calculate_statistics:
    _type: simple_calculate_statistics
```

Interpretation integration :

- la classe config ne contient pas encore la logique metier
- elle sert de contrat entre le code Python et la configuration YAML
- le nom doit etre stable, explicite et oriente capacite

Decision probable pour notre repo :

- preferer des noms NAT explicites, par exemple :
  - `climate_calculate_statistics`
  - `climate_temperature_anomaly`
  - `climate_country_summary`
- separer le nom YAML local (`calculate_statistics`) du type NAT
  (`climate_calculate_statistics`)

### Step 3 - Wrapper Function / FunctionInfo

Le wrapper connecte la config NAT, les donnees metier et la fonction callable
par l'agent. Exemple du workshop :

```python
from nat.builder.builder import Builder
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function


@register_function(config_type=CalculateStatisticsConfig)
async def calculate_statistics_tool(
    config: CalculateStatisticsConfig,
    builder: Builder,
):
    """Register tool for calculating climate statistics."""
    df = load_climate_data(DATA_PATH)

    async def _wrapper(country: str = "") -> str:
        country_param = None if country == "" else country
        result = calculate_statistics(df, country_param)
        return result

    yield FunctionInfo.from_fn(
        _wrapper,
        input_schema=CalculateStatsInput,
        description=(
            "Calculate temperature statistics globally or for a specific country. "
            "Returns JSON with: mean_temperature (°C), min_temperature (°C), "
            "max_temperature (°C), std_deviation (°C), num_records (count), "
            "trend_per_decade (°C/decade), years_analyzed (e.g. '1950-2025'), "
            "and country (if specified)."
        ),
    )
```

Points importants :

- `@register_function(config_type=...)` enregistre le tool aupres de NAT.
- la fonction de registration recoit `config` et `builder`.
- les donnees peuvent etre chargees une fois au moment de la registration
  (`df = load_climate_data(DATA_PATH)`), puis reutilisees par le wrapper.
- `_wrapper` est async et expose une signature simple au LLM.
- `FunctionInfo.from_fn(...)` relie :
  - la fonction callable
  - le schema d'input Pydantic
  - la description semantique du tool

Point critique :

- la description du tool est un vrai contrat pour l'agent ReAct.
- elle doit indiquer clairement quand utiliser le tool et ce qu'il retourne.
- si la description est vague, l'agent risque de ne pas appeler le tool ou de
  mal interpreter le resultat.

Decision probable pour notre repo :

- separer la logique metier pure de la registration NAT :
  - fonctions pures testables : `calculate_statistics(...)`
  - registration NAT : `calculate_statistics_tool(...)`
- eviter de charger un gros dataset a chaque appel tool
- tester la fonction pure sans LLM ni NAT
- tester le wrapper avec donnees minimales si possible

### Complete minimal registration file from workshop

Le workshop assemble les trois premiers morceaux dans un fichier minimal :

```python
"""This file shows the minimal pattern for registering a Python function as a NAT tool."""

import os
import pandas as pd
from pydantic import BaseModel, Field
from nat.builder.builder import Builder
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function
from nat.data_models.function import FunctionBaseConfig

from .simple_function import calculate_statistics

current_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(
    current_dir,
    "..",
    "..",
    "..",
    "..",
    "resources",
    "climate_data",
    "temperature_annual.csv",
)


def load_climate_data(file_path: str = "temperature_annual.csv") -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df


class CalculateStatsInput(BaseModel):
    country: str = Field(
        default="",
        description=(
            "Country name to filter by (e.g., 'United States', 'France'). "
            "Leave empty for global statistics."
        ),
    )


class CalculateStatisticsConfig(
    FunctionBaseConfig,
    name="simple_calculate_statistics",
):
    """Configuration for calculating climate statistics."""

    pass


@register_function(config_type=CalculateStatisticsConfig)
async def calculate_statistics_tool(
    config: CalculateStatisticsConfig,
    builder: Builder,
):
    """Register tool for calculating climate statistics."""
    df = load_climate_data(DATA_PATH)

    async def _wrapper(country: str = "") -> str:
        country_param = None if country == "" else country
        result = calculate_statistics(df, country_param)
        return result

    yield FunctionInfo.from_fn(
        _wrapper,
        input_schema=CalculateStatsInput,
        description=(
            "Calculate temperature statistics globally or for a specific country. "
            "Returns JSON with: mean_temperature (°C), min_temperature (°C), "
            "max_temperature (°C), std_deviation (°C), num_records (count), "
            "trend_per_decade (°C/decade), years_analyzed (e.g. '1950-2025'), "
            "and country (if specified)."
        ),
    )
```

Integration observations :

- Ce fichier est pedagogique et minimal, pas encore une structure projet finale.
- `DATA_PATH` est construit avec plusieurs `..`; pour notre repo, preferer un
  helper de chemin centralise ou `importlib.resources`.
- `pandas` devient une dependance directe des tools si on conserve ce pattern.
- `load_climate_data(...)` doit etre testee avec un CSV minimal.
- `calculate_statistics(...)` doit rester dans un module separe pour conserver
  une fonction pure, testable sans NAT.
- Le wrapper NAT doit retourner une string stable, idealement JSON.
- La description `FunctionInfo` doit etre traitee comme une interface agent :
  elle guide le choix du tool par le ReAct agent.

Structure cible probable pour adaptation :

```text
src/training_nvidia_nat/
  climate_data.py
  climate_stats.py
  tools/
    climate_statistics.py
tests/
  test_climate_stats.py
  test_climate_tool_registration.py
configs/
  react_climate.yml
```

### Python packaging for NAT

La lecon montre que NAT decouvre les tools via les entry points du package
Python.

Exemple workshop :

```toml
[project]
name = "climate_analyzer"

[project.entry-points.nat]
"climate_analyzer/calculate_statistics" = "climate_analyzer.register"
```

Installation editable :

```bash
uv pip install -e .
```

Interpretation :

- le decorateur `@register_function(...)` ne suffit pas si le module n'est
  jamais importe par NAT
- l'entry point indique a NAT quel module charger pour enregistrer les tools
- le package doit etre installe en editable pour que NAT voie les changements
  locaux pendant le dev

Impact pour notre repo :

- `pyproject.toml` devra ajouter une section `[project.entry-points.nat]`
- le module cible devra importer/definir les fonctions `@register_function`
- notre package est deja installable via `setuptools` et `src/`
- le workflow ReAct/tools devra etre valide apres `pip install -e .`

Decision probable :

```toml
[project.entry-points.nat]
"training_nvidia_nat/climate_statistics" = "training_nvidia_nat.tools.climate_statistics"
```

Point a verifier quand on implemente :

- le format exact attendu par NAT pour la cle d'entry point
- si une fonction `register` explicite est requise ou si l'import du module
  contenant `@register_function` suffit
- compatibilite avec `pip install -e .` deja utilise dans ce projet

### Step 4 - YAML wiring

La configuration YAML relie les tools enregistres au workflow agent. Exemple du
workshop :

```yaml
functions:
  calculate_statistics:
    _type: climate_analyzer/calculate_statistics
    description: "Temperature statistics tool"

  filter_by_country:
    _type: climate_analyzer/filter_by_country

  create_visualization:
    _type: climate_analyzer/create_visualization

workflow:
  _type: react_agent
  llm_name: climate_llm
  tool_names:
    - calculate_statistics
    - filter_by_country
    - create_visualization
```

Interpretation :

- `functions.<local_name>` declare une instance de tool utilisable par le
  workflow.
- `_type` pointe vers le type NAT enregistre via entry point/config class.
- `workflow._type: react_agent` remplace le simple `chat_completion`.
- `tool_names` controle explicitement les tools visibles par l'agent.

Impact pour notre repo :

- garder `config.yml` comme baseline simple `chat_completion`
- ajouter un workflow separe, par exemple `configs/react_climate.yml`
- declarer les tools dans `functions`
- declarer le ReAct agent dans `workflow`
- verifier avec :

```bash
nat validate --config_file configs/react_climate.yml
```

Point critique :

- Les noms dans `tool_names` doivent correspondre aux cles sous `functions`.
- Les `_type` doivent correspondre aux entry points NAT exposes par le package.
- Sans `pip install -e .`, NAT risque de ne pas decouvrir les tools locaux.

### Dependency injection and beyond

La lecon montre que les functions enregistrees peuvent etre reutilisees au-dela
du simple agent :

```yaml
workflow:              # Tools for agents
  tool_names:
    - calculate_statistics

telemetry:             # Automatic tracing
  tracing:
    phoenix:
      _type: phoenix

eval:                  # Systematic evaluation
  evaluators:
    - response_quality
```

Interpretation :

- Les functions NAT deviennent des composants reutilisables dans l'ecosysteme.
- Le workflow agent peut les utiliser comme tools.
- La telemetry peut tracer les appels et les etapes intermediaires.
- L'evaluation peut mesurer la qualite systematiquement.

Impact pour notre objectif GitHub :

- c'est un argument fort d'integration enterprise : agent + observability +
  evaluation dans une meme configuration.
- notre demo initiale peut rester focalisee sur tools/ReAct.
- une phase suivante peut ajouter Phoenix tracing ou un eval minimal pour montrer
  une integration plus complete.

Decision probable :

- phase 1 : baseline `chat_completion`
- phase 2 : ReAct agent + climate tools
- phase 3 : tracing/eval, si le workshop fournit un pattern stable

### NAT workflow scaffolding

La lecon montre que NAT peut generer une structure de workflow :

```bash
nat workflow create climate_assistant
```

Structure generee par le workshop :

```text
pyproject.toml
README.md
src/
  climate_assistant/
    __init__.py
    configs/
      config.yml
    register.py
```

Interpretation :

- `nat workflow create` genere le boilerplate standard d'un package NAT.
- `register.py` devient le point naturel pour les `@register_function`.
- `configs/config.yml` contient la config workflow/package.
- `pyproject.toml` declare les entry points NAT.

Impact pour notre repo :

- ne pas executer le scaffold dans le repo existant sans plan, car nous avons
  deja une structure `src/training_nvidia_nat`.
- utiliser ce scaffold comme reference pour aligner notre structure :

```text
src/training_nvidia_nat/
  __init__.py
  register.py
  configs/
    react_climate.yml
```

ou garder `configs/` a la racine si c'est plus lisible pour le repo demo.

Decision probable :

- eviter de regenerer le projet avec `nat workflow create`
- adapter notre structure existante au pattern NAT
- ajouter un `register.py` dedie quand on implemente les tools

### Climate statistics and visualization outputs

Le workshop montre une fonction metier pure `calculate_statistics(df)` avec une
sortie JSON/string de statistiques globales.

Exemple de sortie :

```json
{
  "mean_temperature": 17.91,
  "min_temperature": -15.71,
  "max_temperature": 29.23,
  "std_deviation": 7.83,
  "num_records": 1210,
  "trend_per_decade": 0.241,
  "years_analyzed": "1950-2025"
}
```

Champs attendus :

- `mean_temperature`
- `min_temperature`
- `max_temperature`
- `std_deviation`
- `num_records`
- `trend_per_decade`
- `years_analyzed`
- `country` si un filtre pays est applique

Tests futurs probables :

- `test_calculate_statistics_global_returns_expected_fields`
- `test_calculate_statistics_country_filter_adds_country`
- `test_calculate_statistics_returns_json_string`

Le workshop montre aussi une fonction de visualisation :

```python
create_visualization(
    df,
    plot_type="annual_trend",
    save_path="global_trend.png",
)
```

Sortie observee :

```text
Created annual_trend plot and saved to global_trend.png
```

Types de visualisation vus :

- `annual_trend`
- `country_comparison`
- `monthly_pattern`

Points d'integration :

- le tool de visualisation produit un artefact fichier, pas seulement du texte
- `save_path` doit etre controle pour eviter les ecritures arbitraires
- le retour doit rester une string exploitable par l'agent
- pour la demo portfolio, ce tool peut produire une preuve visuelle forte

Tests futurs probables :

- `test_create_visualization_writes_file`
- `test_create_visualization_rejects_unknown_plot_type`
- `test_create_visualization_returns_description`

### Multi-tool ReAct workflow

Le workshop etend le workflow ReAct avec plusieurs tools :

```yaml
functions:
  list_countries:
    _type: climate_analyzer/list_countries
    description: "List all available countries in the dataset"

  calculate_statistics:
    _type: climate_analyzer/calculate_statistics
    description: "Calculate temperature statistics globally or for a specific country"

  filter_by_country:
    _type: climate_analyzer/filter_by_country
    description: "Get information about climate data for a specific country"

  find_extreme_years:
    _type: climate_analyzer/find_extreme_years
    description: "Find the warmest or coldest years in the dataset"

  create_visualization:
    _type: climate_analyzer/create_visualization
    description: "Create visualizations including automatic top 5 countries by warming"

workflow:
  _type: react_agent
  tool_names:
    - list_countries
    - calculate_statistics
    - filter_by_country
    - find_extreme_years
    - create_visualization
  llm_name: climate_llm
  verbose: true
  max_iterations: 5
  parse_agent_response_max_retries: 2
```

Interpretation :

- `functions` declare les tools disponibles dans la config NAT.
- `tool_names` choisit explicitement les tools exposes au ReAct agent.
- `verbose: true` rend les etapes ReAct observables pendant le dev.
- `max_iterations: 5` limite les cycles thought/action/observation.
- `parse_agent_response_max_retries: 2` rend l'agent plus robuste si sa sortie
  n'est pas parsable.

Point critique observe avec le tool unique :

- l'agent peut passer `None` comme input quand il veut des statistiques globales.
- le wrapper ou la fonction metier doit traiter `None`, `""` et `"None"` comme
  absence de filtre pays.

Decision probable pour notre repo :

- demarrer avec un seul tool propre et teste (`calculate_statistics`)
- ajouter ensuite les tools par capacite :
  - `list_countries`
  - `filter_by_country`
  - `find_extreme_years`
  - `create_visualization`
- chaque tool doit avoir :
  - fonction pure testee
  - schema Pydantic
  - config class NAT
  - wrapper NAT
  - reference YAML
- ajouter des tests pour les inputs ambigus generes par le LLM (`None`, vide,
  pays inexistant)

## Lesson - Phoenix observability

La lecon suivante ajoute Phoenix comme backend d'observability pour tracer les
workflows NAT.

Objectif conceptuel :

```text
NAT workflow -> tracer -> telemetry -> Phoenix exporter
```

Ce que Phoenix permet d'observer :

- appels LLM
- appels tools
- acces memoire
- retrievers
- fonctions imbriquees
- erreurs
- latence
- etapes intermediaires d'un agent ReAct

Pattern YAML observe :

```yaml
general:
  telemetry:
    tracing:
      phoenix:
        _type: phoenix
        endpoint: http://localhost:6006/v1/traces
        project: climate_analyzer_baseline
```

Interpretation :

- `general.telemetry.tracing` configure le tracing global NAT.
- `_type: phoenix` selectionne l'exporter Phoenix.
- `endpoint` pointe vers l'ingestion traces Phoenix.
- `project` groupe les traces dans Phoenix.

Impact pour notre repo :

- creer/maintenir une note dediee :
  `docs/nat-phoenix-observability-lesson.md`
- ajouter plus tard une config observee :
  `configs/react_climate_phoenix.yml`
- utiliser des noms de projet Phoenix distincts pour comparer :
  - baseline
  - react tools
  - optimized

Setup observe dans le workshop :

```bash
cd climate_analyzer
uv pip install -e .
cd ..
phoenix serve
```

Equivalent local probable :

```bash
python -m pip install -e .
phoenix serve
```

URLs locales :

```text
Phoenix UI: http://localhost:6006
Trace endpoint: http://localhost:6006/v1/traces
```

Note :

- le JS du lab qui remplace `p3000` par `p6006` sert uniquement dans
  l'environnement notebook heberge.
- en local, ouvrir directement `http://localhost:6006`.

Decision d'implementation dans ce repo :

- `nat info components --types tracing --query phoenix --num_results 20`
  retourne aucun composant `phoenix` dans le venv actuel.
- NAT 1.7.0 expose en revanche l'exporter OpenTelemetry `otelcollector`.
- Phoenix accepte les traces OTLP HTTP sur `http://localhost:6006/v1/traces`.
- La config implementee est donc :

```yaml
general:
  telemetry:
    tracing:
      phoenix_local:
        _type: otelcollector
        endpoint: http://localhost:6006/v1/traces
        project: training_nvidia_nat_react_climate
```

Commandes implementees :

```bash
scripts/serve_phoenix.sh
NAT_CONFIG_FILE=configs/react_climate_phoenix.yml scripts/serve_react_backend.sh
scripts/serve_ui.sh
```

Validation actuelle :

```bash
scripts/validate_local.sh
```

Cette validation couvre maintenant :

- `config.yml`
- `configs/react_climate.yml`
- `configs/react_climate_phoenix.yml`
- tests unitaires
- Ruff
- syntaxe shell

## Next learning state - multi-agent LangGraph math

Lien formation :

```text
https://learn.deeplearning.ai/courses/nvidia-nat-making-agents-reliable/lesson/cni196/multi-agent-integration-adding-math
```

Ce que la lecon montre :

- integrer un agent LangGraph calculator comme tool NAT
- le rendre disponible au climate ReAct agent
- utiliser `framework_wrappers=[LLMFrameworkEnum.LANGCHAIN]`
- recuperer le LLM du calculator via le `builder` NAT et la config YAML
- eviter de hardcoder le model dans le code LangGraph

Representation physique dans notre repo :

```text
src/training_nvidia_nat/calculator_agent.py
  -> construit/compile un petit graph LangGraph

src/training_nvidia_nat/register.py
  -> wrappe ce graph comme function/tool NAT

configs/react_climate_math.yml
  -> declare calculator_llm + calculator_agent

configs/react_climate_phoenix_math.yml
  -> meme chose avec tracing Phoenix
```

Pattern attendu :

```python
@register_function(
    config_type=CalculatorAgentConfig,
    framework_wrappers=[LLMFrameworkEnum.LANGCHAIN],
)
async def calculator_agent_tool(config: CalculatorAgentConfig, builder: Builder):
    llm = await builder.get_llm(
        config.llm_name,
        wrapper_type=LLMFrameworkEnum.LANGCHAIN,
    )
    agent = build_calculator_agent(llm)

    async def _wrapper(inputs: CalculatorInput) -> str:
        result = await agent.ainvoke(...)
        return ...

    yield FunctionInfo.from_fn(...)
```

Demo cible :

```text
For India, use the observed temperature trend per decade to project the average
temperature in 2050. Explain the calculation.
```

Flux attendu :

```text
climate ReAct agent
  -> calculate_statistics(country="India")
  -> calculator_agent
       -> LangGraph calculator sub-agent
  -> final answer
```

Ce que ca montre :

- NAT orchestre un agent principal + un sous-agent LangGraph.
- Les tools simples restent dans `climate.py`.
- Les calculs avances sont delegues au sub-agent.
- Phoenix doit montrer les appels imbriques.

Decision :

- ne pas copier le helper de la formation
- creer notre propre mini agent LangGraph calculator
- le garder minimal mais reel
- ajouter tests unitaires sur les fonctions math pures si possible

## Future packaging state - Docker Compose

Docker peut aider pour assembler la demo, mais ne remplace pas le venv local
pour l'apprentissage.

Architecture cible :

```text
docker compose
  nat-backend
    -> nat serve --config_file configs/react_climate_phoenix.yml

  phoenix
    -> Phoenix UI http://localhost:6006
    -> OTLP HTTP http://localhost:6006/v1/traces

  nat-ui
    -> official NVIDIA NAT UI
    -> talks to nat-backend
```

Interet :

- une commande unique pour la demo GitHub/portfolio
- ports fixes
- separation claire NAT / Phoenix / UI
- presentation plus professionnelle

Contraintes :

- `NVIDIA_API_KEY` reste obligatoire
- `.env` ne doit jamais etre committe
- ne pas copier/vendor l'UI NVIDIA dans ce repo
- utiliser volume Docker pour Phoenix

Positionnement :

```text
venv local = dev/formation/debug
docker compose = packaging demo reproductible
```
