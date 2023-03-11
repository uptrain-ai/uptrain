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

**Lea esto en otros idiomas**:<kbd>[<img title="English" alt="English language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/us.svg" width="22">](README.md)</kbd><kbd>[<img title="German" alt="German language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/de.svg" width="22">](i18n/README.de.md)</kbd><kbd>[<img title="Hindi" alt="Hindi language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/in.svg" width="22">](i18n/README.hi.md)</kbd><kbd>[<img title="Spanish" alt="Spanish language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/es.svg" width="22">](i18n/README.es.md)</kbd><kbd>[<img title="French" alt="French language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/fr.svg" width="22">](i18n/README.fr.md)</kbd><kbd>[<img title="Japanese" alt="Japanese language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/jp.svg" width="22">](i18n/README.ja.md)</kbd>

-   [Alemán](README.de.md)

**[UpTrain](https://uptrain.ai)**es una herramienta segura de datos de código abierto para que los profesionales de ML observen y perfeccionen sus modelos de ML al monitorear su rendimiento, verificar los cambios de distribución (de datos) y recopilar casos extremos para volver a capacitarlos. Se integra a la perfección con sus canales de producción existentes y solo toma unos minutos para comenzar ⚡.

<h4>
</h4>
<h4> </h4>

# **[Características clave](https://uptrain.gitbook.io/docs/what-is-uptrain/key-features)**💡

-   **[Comprobaciones de deriva de datos](https://docs.uptrain.ai/docs/uptrain-monitors/data-drift)**- Identifique los cambios de distribución en las entradas de su modelo.
-   **[Supervisión del rendimiento](https://docs.uptrain.ai/docs/uptrain-monitors/concept-drift)**- Realice un seguimiento del rendimiento de sus modelos en tiempo real y reciba alertas de degradación.
-   **[Soporte de incrustaciones](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)**- Tableros especializados para comprender las incrustaciones deducidas del modelo.
-   **[Señales de caso de borde](https://docs.uptrain.ai/docs/uptrain-monitors/edge-case-detection)**- Señales definidas por el usuario y técnicas estadísticas para detectar puntos de datos fuera de distribución.
-   **[Comprobaciones de integridad de datos](https://docs.uptrain.ai/docs/uptrain-monitors/data-integrity)**- Comprobaciones de datos faltantes o incoherentes, registros duplicados, calidad de los datos, etc.
-   **[Métricas personalizables](https://docs.uptrain.ai/docs/monitoring-custom-metrics)**- Defina métricas personalizadas que tengan sentido para su caso de uso.
-   **[Reciclaje automatizado](https://github.com/uptrain-ai/uptrain/blob/main/examples/human_orientation_classification/deepdive_examples/uptrain_check_all.ipynb)**- Automatice el reentrenamiento de modelos adjuntando sus canalizaciones de entrenamiento e inferencia.
-   **[Sesgo del modelo](https://docs.uptrain.ai/docs/uptrain-monitors/model-bias)**- Realice un seguimiento del sesgo en las predicciones de su modelo ML.
-   **[Explicabilidad de la IA](https://docs.uptrain.ai/docs/uptrain-visuals/shap-explainability)**- Comprender la importancia relativa de múltiples características en las predicciones.
-   **Seguridad de datos**- Sus datos nunca salen de su máquina.
-   **Integración de holgura**- Recibe alertas en Slack.
-   **Tableros en tiempo real**- Para visualizar la salud de tu modelo en vivo.

## 🚨Próximamente🚨

-   **Cambio de etiqueta**- Identificar desviaciones en sus predicciones. Especialmente útil en los casos en que la verdad del terreno no está disponible.
-   **Intervalo de confianza del modelo**- Intervalos de confianza para las predicciones del modelo
-   **Técnicas avanzadas de detección de deriva**- Métodos de detección de deriva basados ​​en valores atípicos
-   **Rebanado de características avanzadas**- Capacidad para dividir propiedades estadísticas
-   **Prueba de Kolmogorov-Smirnov**- Para la detección de turnos de distribución
-   **Estabilidad de predicción**- Filtrar casos donde la predicción del modelo no es estable.
-   **Cheques contradictorios**- Combatir los ataques adversarios

Y más.

<h4> </h4>

# Empieza 🙌

Puede comenzar rápidamente con[Colaboración de Google aquí](https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing%2F).

Para ejecutarlo en su máquina, siga los pasos a continuación:

### Instale el paquete a través de pip:

```console
pip install uptrain
```

### Ejecuta tu primer ejemplo:

```console
git clone git@github.com:uptrain-ai/uptrain.git
cd uptrain/examples
pip install jupyterlab
jupyter lab
```

Para obtener una descripción general rápida de cómo funciona UpTrain, consulte nuestro[tutorial de inicio rápido](https://docs.uptrain.ai/docs/uptrain-examples/quickstart-tutorial).

<h4> </h4>

# UpTrain en[acción](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)🎬

Uno de los casos de uso más comunes de ML en la actualidad son los modelos de lenguaje, ya sea resumen de texto, NER, chatbots, traducción de idiomas, etc. UpTrain proporciona formas de visualizar las diferencias en la capacitación y los datos del mundo real a través de la agrupación UMAP de incrustaciones de texto (inferidos). de Berto). Las siguientes son algunas repeticiones del tablero de UpTrain.

### AI Explicabilidad lista para usar

<h1 align="left">
<img alt="umap_gif" width="60%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/ride_estimation/4_Explanability_recording.gif">
</h1>

### Supervisión del rendimiento del modelo en vivo y comprobaciones de integridad de datos

<h1 align="left">
<img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/fraud_detection/concept_drift_avg_acc.gif"> <img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/finetuning_llms/data_integrity.gif">
</h1>

### Reducción y Visualización de Dimensionalidad UMAP

<h1 align="left">
<img alt="umap_gif" width="60%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/text_summarization/umap.gif">
</h1>

### Colección Edge-case para ajustar el modelo más tarde

<h1 align="left">
<img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/finetuning_llms/edge_cases.gif">
</h1>

# ¿Por qué UpTrain 🤔?

Los modelos de aprendizaje automático (ML) se utilizan ampliamente para tomar decisiones comerciales críticas. Aún así, ningún modelo de ML es 100 % preciso y, además, su precisión se deteriora con el tiempo 😣. Por ejemplo, la predicción de ventas se vuelve imprecisa con el tiempo debido a un cambio en los hábitos de compra de los consumidores. Además, debido a la naturaleza de caja negra de los modelos de ML, es un desafío identificar y solucionar sus problemas.

UpTrain resuelve esto. Hacemos que sea fácil para los científicos de datos y los ingenieros de ML comprender dónde fallan sus modelos y ayudarlos a corregirlos antes de que otros se quejen 🗣️.

UpTrain se puede utilizar para una amplia variedad de modelos de aprendizaje automático, como LLM, modelos de recomendación, modelos de predicción, modelos de visión artificial, etc.

Trabajamos constantemente para mejorar UpTrain. ¿Quieres una nueva función o necesitas alguna integración? No dude en[crear un problema](https://github.com/uptrain-ai/uptrain/issues)o[contribuir](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md)directamente al repositorio.

<h1 align="center">
<img alt="Meme" width="40%" src="https://user-images.githubusercontent.com/108270398/215209245-4d6b1f47-7af9-4db8-8d8c-63dcc610571c.jpg">
</h1>

# Licencia 💻

Este repositorio se publica bajo licencia Apache 2.0. Actualmente estamos enfocados en desarrollar ofertas no empresariales que deberían cubrir la mayoría de los casos de uso al agregar más funciones y extendernos a más modelos. También estamos trabajando para agregar una oferta alojada:[Contáctenos](mailto:sourabh@insane.ai)si estás interesado.

# Mantente actualizado ☎️

Estamos continuamente agregando toneladas de características y casos de uso. ¡Apóyanos dándole una estrella al proyecto ⭐!

# Proporcione comentarios (cuanto más duro, mejor 😉)

Estamos construyendo UpTrain en público. Ayúdanos a mejorar dando tu opinión**[aquí](https://forms.gle/PXd89D5LiFubro9o9)**.

# Colaboradores 🖥️

Damos la bienvenida a las contribuciones para mejorar. Por favor vea nuestro[guía de contribución](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md)para detalles.

<a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=uptrain-ai/uptrain" />
</a>
