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

**Lesen Sie dies in anderen Sprachen**: 
<kbd>[<img title="English" alt="English language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/us.svg" width="22">](/README.md)</kbd>
<kbd>[<img title="German" alt="German language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/de.svg" width="22">](/i18n/README.de.md)</kbd>
<kbd>[<img title="Chinese" alt="Chinese language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/cn.svg" width="22">](/i18n/README.zh-CN.md)</kbd>
<kbd>[<img title="Hindi" alt="Hindi language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/in.svg" width="22">](/i18n/README.hi.md)</kbd>
<kbd>[<img title="Spanish" alt="Spanish language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/es.svg" width="22">](/i18n/README.es.md)</kbd>
<kbd>[<img title="French" alt="French language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/fr.svg" width="22">](/i18n/README.fr.md)</kbd>
<kbd>[<img title="Japanese" alt="Japanese language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/jp.svg" width="22">](/i18n/README.ja.md)</kbd>
<kbd>[<img title="Russian" alt="Russian language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/ru.svg" width="22">](/i18n/README.ru.md)</kbd>


**[UpTrain](https://uptrain.ai)** ist ein datensicheres Open-Source-Tool für ML-Praktiker, um ihre ML-Modelle zu beobachten und zu verfeinern, indem sie ihre Leistung überwachen, auf (Daten-)Verteilungsverschiebungen prüfen und Grenzfälle sammeln, um sie neu zu schulen. Es lässt sich nahtlos in Ihre bestehenden Produktionspipelines integrieren und ist in wenigen Minuten einsatzbereit ⚡.


# **[Hauptmerkmale](https://uptrain.gitbook.io/docs/what-is-uptrain/key-features)** 💡

-   **[Datendrift-Checks](https://docs.uptrain.ai/docs/uptrain-monitors/data-drift)** - Identifizieren Sie Verteilungsverschiebungen in Ihren Modelleingaben.
-   **[Leistungsüberwachung](https://docs.uptrain.ai/docs/uptrain-monitors/concept-drift)** - Verfolgen Sie die Leistung Ihrer Modelle in Echtzeit und erhalten Sie Verschlechterungswarnungen.
-   **[Einbettungsunterstützung](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)** - Spezialisierte Dashboards zum Verständnis der vom Modell abgeleiteten Einbettungen.
-   **[Edge-Case-Signale](https://docs.uptrain.ai/docs/uptrain-monitors/edge-case-detection)** - Benutzerdefinierte Signale und statistische Techniken zur Erkennung von Datenpunkten außerhalb der Verteilung.
-   **[Datenintegritätsprüfungen](https://docs.uptrain.ai/docs/uptrain-monitors/data-integrity)** - Überprüfung auf fehlende oder inkonsistente Daten, doppelte Aufzeichnungen, Datenqualität usw.
-   **[Customizable metrics](https://docs.uptrain.ai/docs/monitoring-custom-metrics)** - Definieren Sie benutzerdefinierte Metriken, die für Ihren Anwendungsfall sinnvoll sind.
-   **[Automatisierte Umschulung](https://github.com/uptrain-ai/uptrain/blob/main/examples/human_orientation_classification/deepdive_examples/uptrain_check_all.ipynb)** - Automatisieren Sie das Neutraining von Modellen, indem Sie Ihre Trainings- und Inferenz-Pipelines anhängen.
-   **[Modellverzerrung](https://docs.uptrain.ai/docs/uptrain-monitors/model-bias)** - Verfolgen Sie Verzerrungen in den Vorhersagen Ihres ML-Modells.
-   **[KI-Erklärbarkeit](https://docs.uptrain.ai/docs/uptrain-visuals/shap-explainability)** - Verstehen Sie die relative Bedeutung mehrerer Merkmale für Vorhersagen.
-   **Datensicherheit** - Ihre Daten verlassen niemals Ihre Maschine.
-   **Slack-Integration** - Erhalten Sie Benachrichtigungen zu Slack.
-   **Echtzeit-Dashboards** - Um die Gesundheit Ihres Modells live zu visualisieren.

## 🚨Demnächst🚨

-   **Etikettenverschiebung** - Identifizieren Sie Abweichungen in Ihren Vorhersagen. Besonders nützlich in Fällen, in denen Ground Truth nicht verfügbar ist.
-   **Modellkonfidenzintervall** - Konfidenzintervalle für Modellvorhersagen
-   **Fortgeschrittene Drifterkennungstechniken** - Ausreißerbasierte Drifterkennungsmethoden
-   **Erweitertes Feature-Slicing** - Fähigkeit, statistische Eigenschaften aufzuteilen
-   **Kolmogorov-Smirnov-Test** - Zur Erkennung von Verteilungsverschiebungen
-   **Vorhersagestabilität** - Filtern Sie Fälle, in denen die Modellvorhersage nicht stabil ist.
-   **Kontradiktorische Kontrollen** - Bekämpfe gegnerische Angriffe

Und mehr.


# Fang an 🙌

Sie können schnell loslegen [Google Colab hier](https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing%2F).

Führen Sie die folgenden Schritte aus, um es auf Ihrem Computer auszuführen:

### Installieren Sie das Paket über Pip:

```console
pip install uptrain
```

### Führen Sie Ihr erstes Beispiel aus:

```console
git clone git@github.com:uptrain-ai/uptrain.git
cd uptrain/examples
pip install jupyterlab
jupyter lab
```

Eine kurze Anleitung zur Funktionsweise von UpTrain finden Sie in unserem [Schnellstart-Tutorial](https://docs.uptrain.ai/docs/uptrain-examples/quickstart-tutorial).


# UpTrain ein [Aktion](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)🎬

Einer der häufigsten Anwendungsfälle von ML sind heute Sprachmodelle, sei es Textzusammenfassung, NER, Chatbots, Sprachübersetzung usw. UpTrain bietet Möglichkeiten zur Visualisierung von Unterschieden in den Trainings- und realen Daten über UMAP-Clustering von Texteinbettungen (inferred von Bert). Es folgen einige Wiederholungen aus dem UpTrain-Dashboard.

### KI-Erklärbarkeit out-of-the-box

<h1 align="left">
<img alt="umap_gif" width="60%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/ride_estimation/4_Explanability_recording.gif">
</h1>

### Live-Modellleistungsüberwachung und Datenintegritätsprüfungen

<h1 align="left">
<img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/fraud_detection/concept_drift_avg_acc.gif"> <img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/finetuning_llms/data_integrity.gif">
</h1>

### UMAP-Dimensionsreduktion und Visualisierung

<h1 align="left">
<img alt="umap_gif" width="60%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/text_summarization/umap.gif">
</h1>

### Edge-Case-Sammlung zur späteren Feinabstimmung des Modells

<h1 align="left">
<img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/finetuning_llms/edge_cases.gif">
</h1>

# Warum UpTrain 🤔?

Modelle für maschinelles Lernen (ML) werden häufig verwendet, um wichtige Geschäftsentscheidungen zu treffen. Dennoch ist kein ML-Modell zu 100 % genau, und außerdem nimmt seine Genauigkeit mit der Zeit ab 😣. Beispielsweise wird die Verkaufsvorhersage im Laufe der Zeit aufgrund einer Änderung der Kaufgewohnheiten der Verbraucher ungenau. Darüber hinaus ist es aufgrund der Black-Box-Natur von ML-Modellen schwierig, ihre Probleme zu identifizieren und zu beheben.

UpTrain löst dies. Wir machen es Data Scientists und ML-Ingenieuren leicht zu verstehen, wo ihre Modelle schief gehen, und helfen ihnen, sie zu beheben, bevor sich andere beschweren 🗣️.

UpTrain kann für eine Vielzahl von maschinellen Lernmodellen wie LLMs, Empfehlungsmodelle, Vorhersagemodelle, Computer-Vision-Modelle usw. verwendet werden.

Wir arbeiten ständig daran, UpTrain besser zu machen. Möchten Sie eine neue Funktion oder benötigen Sie Integrationen? Fühlen sich frei [create an issue](https://github.com/uptrain-ai/uptrain/issues) oder [beitragen](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) direkt ins Depot.

<h1 align="center">
<img alt="Meme" width="40%" src="https://user-images.githubusercontent.com/108270398/215209245-4d6b1f47-7af9-4db8-8d8c-63dcc610571c.jpg">
</h1>

# Lizenz 💻

Dieses Repo wird unter der Apache 2.0-Lizenz veröffentlicht. Wir konzentrieren uns derzeit auf die Entwicklung von Nicht-Unternehmensangeboten, die die meisten Anwendungsfälle abdecken sollten, indem wir mehr Funktionen hinzufügen und auf mehr Modelle ausdehnen. Wir arbeiten auch daran, ein gehostetes Angebot hinzuzufügen - [kontaktiere uns](mailto:sourabh@insane.ai) wenn Sie interessiert sind.

# Stay Updated ☎️

Wir fügen kontinuierlich Tonnen von Funktionen und Anwendungsfällen hinzu. Bitte unterstützen Sie uns, indem Sie dem Projekt einen Stern ⭐ geben!

# Feedback geben (härter desto besser 😉)

Wir bauen UpTrain öffentlich auf. Helfen Sie uns, uns zu verbessern, indem Sie Ihr Feedback geben **[Hier](https://forms.gle/PXd89D5LiFubro9o9)**.

# Mitwirkende 🖥️

Wir freuen uns über Beiträge zu uptrain. Bitte sehen Sie sich unsere an [Beitragsleitfaden](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) für Details.

<a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=uptrain-ai/uptrain" />
</a>
