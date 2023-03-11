<h4 align="center">
  <a href="https://uptrain.ai">
    <img width="300" src="https://user-images.githubusercontent.com/108270398/214240695-4f958b76-c993-4ddd-8de6-8668f4d0da84.png" alt="uptrain">
  </a>
</h4>
<h2>
  <p align="center">
    <p align="center">An open-source framework to observe ML applications, built for engineers</p>
  </p>
</h2>

<p align="center">
<a href="https://docs.uptrain.ai/docs/" rel="nofollow"><strong>Docs</strong></a>
-
<a href="https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing/" rel="nofollow"><strong>Try it out</strong></a>
-
<a href="https://discord.com/invite/gVvZhhrQaQ/" rel="nofollow"><strong>Support Community</strong></a>
-
<a href="https://github.com/uptrain-ai/uptrain/issues/new?assignees=&labels=bug&template=bug_report.md&title=" rel="nofollow"><strong>Bug Report</strong></a>
-
<a href="https://github.com/uptrain-ai/uptrain/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=" rel="nofollow"><strong>Feature Request</strong></a>
</p>

<h4 align="center">
  <a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/uptrain-ai/uptrain">
  </a>
  <a href='https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md'>
    <img alt='PRs Welcome' src='https://img.shields.io/badge/PRs-welcome-orange.svg?style=shields'/>
  </a>
  <a href="https://github.com/uptrain-ai/uptrain/commits/main">
    <img src="https://img.shields.io/github/commit-activity/m/uptrain-ai/uptrain"  />
  </a>
  <a href="https://docs.uptrain.ai/docs/">
    <img src="https://img.shields.io/badge/Read-Docs-brightgreen" alt="Docs" />
  </a>
  <a href="https://discord.com/invite/gVvZhhrQaQ">
    <img src="https://img.shields.io/badge/Discord-Community-orange" alt="Community" />
  </a>
  <a href="https://uptrain.ai/">
    <img src="https://img.shields.io/badge/UpTrain-Website-yellow" alt="Website" />
  </a>
  <a href="https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing/">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
  </a>
</h4>

<h4 align="center">
<img src="https://uptrain-demo.s3.us-west-1.amazonaws.com/human_orientation_classification/1_data_drift_and_edge_cases.gif" width="85%" alt="Performance" />
</h4>

<h4>
</h4>

**Lire ceci dans d'autres langues**:<kbd>[<img title="English" alt="English language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/us.svg" width="22">](/README.md)</kbd><kbd>[<img title="German" alt="German language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/de.svg" width="22">](/i18n/README.de.md)</kbd><kbd>[<img title="Hindi" alt="Hindi language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/in.svg" width="22">](/i18n/README.hi.md)</kbd><kbd>[<img title="Spanish" alt="Spanish language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/es.svg" width="22">](/i18n/README.es.md)</kbd><kbd>[<img title="French" alt="French language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/fr.svg" width="22">](/i18n/README.fr.md)</kbd><kbd>[<img title="Japanese" alt="Japanese language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/jp.svg" width="22">](/i18n/README.ja.md)</kbd><kbd>[<img title="Korean" alt="Korean language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/kr.svg" width="22">](i18n/README.ko.md)</kbd>

**[UpTrain](https://uptrain.ai)**est un outil open source sécurisé pour les données permettant aux praticiens du ML d'observer et d'affiner leurs modèles de ML en surveillant leurs performances, en vérifiant les changements de distribution (de données) et en collectant des cas extrêmes pour les recycler. Il s'intègre parfaitement à vos pipelines de production existants et ne prend que quelques minutes pour démarrer ⚡.

<h4>
</h4>
<h4> </h4>

# **[Principales caractéristiques](https://uptrain.gitbook.io/docs/what-is-uptrain/key-features)**💡

-   **[Contrôles de dérive des données](https://docs.uptrain.ai/docs/uptrain-monitors/data-drift)**- Identifiez les changements de distribution dans les entrées de votre modèle.
-   **[Suivi de la performance](https://docs.uptrain.ai/docs/uptrain-monitors/concept-drift)**- Suivez les performances de vos modèles en temps réel et recevez des alertes de dégradation.
-   **[Prise en charge des incorporations](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)**- Tableaux de bord spécialisés pour comprendre les intégrations induites par le modèle.
-   **[Signaux de cas extrêmes](https://docs.uptrain.ai/docs/uptrain-monitors/edge-case-detection)**- Signaux définis par l'utilisateur et techniques statistiques pour détecter les points de données hors distribution.
-   **[Vérifications de l'intégrité des données](https://docs.uptrain.ai/docs/uptrain-monitors/data-integrity)**- Vérifie les données manquantes ou incohérentes, les enregistrements en double, la qualité des données, etc.
-   **[Métriques personnalisables](https://docs.uptrain.ai/docs/monitoring-custom-metrics)**- Définissez des métriques personnalisées adaptées à votre cas d'utilisation.
-   **[Recyclage automatisé](https://github.com/uptrain-ai/uptrain/blob/main/examples/human_orientation_classification/deepdive_examples/uptrain_check_all.ipynb)**- Automatisez le recyclage des modèles en associant vos pipelines de formation et d'inférence.
-   **[Biais du modèle](https://docs.uptrain.ai/docs/uptrain-monitors/model-bias)**- Suivez les biais dans les prédictions de votre modèle ML.
-   **[Explicabilité de l'IA](https://docs.uptrain.ai/docs/uptrain-visuals/shap-explainability)**- Comprendre l'importance relative de plusieurs fonctionnalités sur les prédictions.
-   **Sécurité des données**- Vos données ne sortent jamais de votre machine.
-   **Intégration Slack**- Recevez des alertes sur Slack.
-   **Tableaux de bord en temps réel**- Pour visualiser la santé de votre modèle en direct.

## 🚨Prochainement🚨

-   **Décalage d'étiquette**- Identifiez les dérives dans vos prédictions. Particulièrement utile dans les cas où la vérité terrain n'est pas disponible.
-   **Intervalle de confiance du modèle**- Intervalles de confiance pour les prédictions du modèle
-   **Techniques avancées de détection de dérive**- Méthodes de détection de dérive basées sur les valeurs aberrantes
-   **Découpage des fonctionnalités avancées**- Capacité à trancher les propriétés statistiques
-   **Test de Kolmogorov-Smirnov**- Pour détecter les décalages de distribution
-   **Stabilité des prévisions**- Filtrer les cas où la prédiction du modèle n'est pas stable.
-   **Contrôles contradictoires**- Combattre les attaques adverses

Et plus.

<h4> </h4>

# Lancez-vous 🙌

Vous pouvez rapidement démarrer avec[Colab Google ici](https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing%2F).

Pour l'exécuter sur votre machine, suivez les étapes ci-dessous :

### Installez le package via pip :

```console
pip install uptrain
```

### Exécutez votre premier exemple :

```console
git clone git@github.com:uptrain-ai/uptrain.git
cd uptrain/examples
pip install jupyterlab
jupyter lab
```

Pour une présentation rapide du fonctionnement d'UpTrain, consultez notre[tutoriel de démarrage rapide](https://docs.uptrain.ai/docs/uptrain-examples/quickstart-tutorial).

<h4> </h4>

# UpTrain in[action](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)🎬

L'un des cas d'utilisation les plus courants de ML aujourd'hui est les modèles de langage, qu'il s'agisse de résumé de texte, de NER, de chatbots, de traduction de langage, etc. UpTrain fournit des moyens de visualiser les différences dans la formation et les données du monde réel via le regroupement UMAP des incorporations de texte de bert). Voici quelques rediffusions du tableau de bord UpTrain.

### Explicabilité de l'IA prête à l'emploi

<h1 align="left">
<img alt="umap_gif" width="60%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/ride_estimation/4_Explanability_recording.gif">
</h1>

### Surveillance des performances du modèle en direct et vérifications de l'intégrité des données

<h1 align="left">
<img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/fraud_detection/concept_drift_avg_acc.gif"> <img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/finetuning_llms/data_integrity.gif">
</h1>

### Réduction et visualisation de la dimensionnalité UMAP

<h1 align="left">
<img alt="umap_gif" width="60%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/text_summarization/umap.gif">
</h1>

### Collection Edge-case pour affiner le modèle ultérieurement

<h1 align="left">
<img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/finetuning_llms/edge_cases.gif">
</h1>

# Pourquoi UpTrain 🤔 ?

Les modèles d'apprentissage automatique (ML) sont largement utilisés pour prendre des décisions commerciales critiques. Pourtant, aucun modèle ML n'est précis à 100 % et, de plus, leur précision se détériore avec le temps 😣. Par exemple, la prévision des ventes devient imprécise au fil du temps en raison d'un changement dans les habitudes d'achat des consommateurs. De plus, en raison de la nature de la boîte noire des modèles ML, il est difficile d'identifier et de résoudre leurs problèmes.

UpTrain résout ce problème. Nous permettons aux scientifiques des données et aux ingénieurs ML de comprendre facilement où leurs modèles vont mal et les aidons à les corriger avant que d'autres ne se plaignent 🗣️.

UpTrain peut être utilisé pour une grande variété de modèles d'apprentissage automatique tels que les LLM, les modèles de recommandation, les modèles de prédiction, les modèles de vision par ordinateur, etc.

Nous travaillons constamment pour améliorer UpTrain. Vous voulez une nouvelle fonctionnalité ou avez besoin d'intégrations ? Ne hésitez pas à[créer un problème](https://github.com/uptrain-ai/uptrain/issues)ou[contribuer](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md)directement au référentiel.

<h1 align="center">
<img alt="Meme" width="40%" src="https://user-images.githubusercontent.com/108270398/215209245-4d6b1f47-7af9-4db8-8d8c-63dcc610571c.jpg">
</h1>

# Licence 💻

Ce référentiel est publié sous licence Apache 2.0. Nous nous concentrons actuellement sur le développement d'offres non professionnelles qui devraient couvrir la plupart des cas d'utilisation en ajoutant plus de fonctionnalités et en s'étendant à plus de modèles. Nous travaillons également à l'ajout d'une offre hébergée -[Contactez-nous](mailto:sourabh@insane.ai)Si tu es intéressé.

# Restez à jour ☎️

Nous ajoutons continuellement des tonnes de fonctionnalités et de cas d'utilisation. Merci de nous soutenir en donnant au projet une étoile ⭐ !

# Donnez votre avis (Plus c'est dur, mieux c'est 😉)

Nous construisons UpTrain en public. Aidez-nous à nous améliorer en donnant votre avis**[ici](https://forms.gle/PXd89D5LiFubro9o9)**.

# Contributeurs 🖥️

Nous accueillons les contributions à uptrain. Veuillez consulter notre[guide des cotisations](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md)pour plus de détails.

<a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=uptrain-ai/uptrain" />
</a>
