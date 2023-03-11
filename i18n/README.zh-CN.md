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

**阅读其他语言版本**:<kbd>[<img title="English" alt="English language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/us.svg" width="22">](README.md)</kbd><kbd>[<img title="German" alt="German language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/de.svg" width="22">](i18n/README.de.md)</kbd><kbd>[<img title="Hindi" alt="Hindi language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/in.svg" width="22">](i18n/README.hi.md)</kbd><kbd>[<img title="Spanish" alt="Spanish language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/es.svg" width="22">](i18n/README.es.md)</kbd><kbd>[<img title="French" alt="French language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/fr.svg" width="22">](i18n/README.fr.md)</kbd><kbd>[<img title="Japanese" alt="Japanese language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/jp.svg" width="22">](i18n/README.ja.md)</kbd><kbd>[<img title="Korean" alt="Korean language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/kr.svg" width="22">](i18n/README.ko.md)</kbd>

**[上行列车](https://uptrain.ai)**是一种开源、数据安全的工具，供 ML 从业者通过监控其性能、检查（数据）分布变化以及收集边缘案例以对其进行再培训来观察和改进其 ML 模型。它与您现有的生产管道无缝集成，只需几分钟即可开始使用 ⚡。

<h4>
</h4>
<h4> </h4>

# **[主要特征](https://uptrain.gitbook.io/docs/what-is-uptrain/key-features)**💡

-   **[数据漂移检查](https://docs.uptrain.ai/docs/uptrain-monitors/data-drift)**- 确定模型输入中的分布变化。
-   **[性能监控](https://docs.uptrain.ai/docs/uptrain-monitors/concept-drift)**- 实时跟踪模型的性能并获得退化警报。
-   **[嵌入支持](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)**- 用于了解模型推断嵌入的专用仪表板。
-   **[边缘案例信号](https://docs.uptrain.ai/docs/uptrain-monitors/edge-case-detection)**- 用户定义的信号和统计技术来检测分布外的数据点。
-   **[数据完整性检查](https://docs.uptrain.ai/docs/uptrain-monitors/data-integrity)**- 检查缺失或不一致的数据、重复记录、数据质量等。
-   **[可定制指标](https://docs.uptrain.ai/docs/monitoring-custom-metrics)**- 定义对您的用例有意义的自定义指标。
-   **[自动再培训](https://github.com/uptrain-ai/uptrain/blob/main/examples/human_orientation_classification/deepdive_examples/uptrain_check_all.ipynb)**- 通过附加您的训练和推理管道来自动进行模型再训练。
-   **[模型偏差](https://docs.uptrain.ai/docs/uptrain-monitors/model-bias)**- 跟踪 ML 模型预测中的偏差。
-   **[人工智能可解释性](https://docs.uptrain.ai/docs/uptrain-visuals/shap-explainability)**- 了解多个特征对预测的相对重要性。
-   **数据安全**- 您的数据永远不会离开您的机器。
-   **松弛集成**- 在 Slack 上获取提醒。
-   **实时仪表板**- 实时可视化模型的健康状况。

## 🚨即将推出🚨

-   **标签转移**- 识别预测中的漂移。在地面实况不可用的情况下特别有用。
-   **模型置信区间**- 模型预测的置信区间
-   **先进的漂移检测技术**- 基于异常值的漂移检测方法
-   **高级特征切片**- 能够切片统计属性
-   **柯尔莫哥洛夫-斯米尔诺夫检验**- 用于检测分布变化
-   **预测稳定性**- 过滤模型预测不稳定的情况。
-   **对抗性检查**- 对抗对抗性攻击

和更多。

<h4> </h4>

# 开始🙌

您可以快速上手[谷歌协作在这里](https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing%2F).

要在您的机器上运行它，请按照以下步骤操作：

### 通过 pip 安装包：

```console
pip install uptrain
```

### 运行你的第一个例子：

```console
git clone git@github.com:uptrain-ai/uptrain.git
cd uptrain/examples
pip install jupyterlab
jupyter lab
```

要快速了解 UpTrain 的工作原理，请查看我们的[快速入门教程](https://docs.uptrain.ai/docs/uptrain-examples/quickstart-tutorial).

<h4> </h4>

# 训练在[行动](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)🎬

当今 ML 最常见的用例之一是语言模型，无论是文本摘要、NER、聊天机器人、语言翻译等。UpTrain 提供了通过文本嵌入的 UMAP 聚类来可视化训练和真实世界数据差异的方法（推断来自伯特）。以下是 UpTrain 仪表板的一些重播。

### 开箱即用的 AI 可解释性

<h1 align="left">
<img alt="umap_gif" width="60%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/ride_estimation/4_Explanability_recording.gif">
</h1>

### 实时模型性能监控和数据完整性检查

<h1 align="left">
<img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/fraud_detection/concept_drift_avg_acc.gif"> <img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/finetuning_llms/data_integrity.gif">
</h1>

### UMAP 降维与可视化

<h1 align="left">
<img alt="umap_gif" width="60%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/text_summarization/umap.gif">
</h1>

### 用于稍后微调模型的边缘案例集合

<h1 align="left">
<img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/finetuning_llms/edge_cases.gif">
</h1>

# 为什么选择 UpTrain🤔？

机器学习 (ML) 模型广泛用于制定关键业务决策。尽管如此，没有 ML 模型是 100% 准确的，而且，它们的准确度会随着时间的推移而下降😣。例如，由于消费者购买习惯的转变，销售预测会随着时间的推移变得不准确。此外，由于 ML 模型的黑盒性质，识别和修复它们的问题具有挑战性。

UpTrain 解决了这个问题。我们让数据科学家和 ML 工程师很容易了解他们的模型哪里出了问题，并帮助他们在其他人抱怨之前修复它们 🗣️。

UpTrain 可用于各种机器学习模型，例如 LLM、推荐模型、预测模型、计算机视觉模型等。

我们一直在努力让 UpTrain 变得更好。想要新功能或需要任何集成？随意地[创建一个问题](https://github.com/uptrain-ai/uptrain/issues)或者[贡献](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md)直接到存储库。

<h1 align="center">
<img alt="Meme" width="40%" src="https://user-images.githubusercontent.com/108270398/215209245-4d6b1f47-7af9-4db8-8d8c-63dcc610571c.jpg">
</h1>

# 执照💻

这个 repo 是在 Apache 2.0 许可下发布的。我们目前专注于开发非企业产品，通过添加更多功能和扩展到更多模型来覆盖大多数用例。我们还致力于添加托管产品 -[联系我们](mailto:sourabh@insane.ai)如果你感兴趣。

# 保持更新 ☎️

我们不断添加大量功能和用例。请给项目打星支持我们⭐！

# 提供反馈（越严厉越好😉）

我们正在公开构建 UpTrain。通过提供您的反馈帮助我们改进**[这里](https://forms.gle/PXd89D5LiFubro9o9)**.

# 贡献者🖥️

我们欢迎对 uptrain 的贡献。请看我们的[投稿指南](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md)了解详情。

<a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=uptrain-ai/uptrain" />
</a>
