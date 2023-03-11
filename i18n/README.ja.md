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


**これを他の言語で読む**: 
<kbd>[<img title="English" alt="English language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/us.svg" width="22">](/README.md)</kbd>
<kbd>[<img title="German" alt="German language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/de.svg" width="22">](/i18n/README.de.md)</kbd>
<kbd>[<img title="Chinese" alt="Chinese language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/jp.svg" width="22">](/i18n/README.zh-CN.md)</kbd>
<kbd>[<img title="Hindi" alt="Hindi language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/in.svg" width="22">](/i18n/README.hi.md)</kbd>
<kbd>[<img title="Spanish" alt="Spanish language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/es.svg" width="22">](/i18n/README.es.md)</kbd>
<kbd>[<img title="French" alt="French language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/fr.svg" width="22">](/i18n/README.fr.md)</kbd>
<kbd>[<img title="Japanese" alt="Japanese language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/jp.svg" width="22">](/i18n/README.ja.md)</kbd>
<kbd>[<img title="Russian" alt="Russian language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/jp.svg" width="22">](/i18n/README.ru.md)</kbd>


**[アップトレイン](https://uptrain.ai)** は、ML 実践者がパフォーマンスを監視し、(データ) 分布シフトをチェックし、エッジ ケースを収集して再トレーニングすることで、ML モデルを観察および改良するためのオープンソースでデータ保護されたツールです。既存の本番パイプラインとシームレスに統合され、数分で開始できます⚡。


# **[主な機能](https://uptrain.gitbook.io/docs/what-is-uptrain/key-features)** 💡

-   **[データドリフトチェック](https://docs.uptrain.ai/docs/uptrain-monitors/data-drift)** - モデル入力の分布シフトを特定します。
-   **[パフォーマンス監視](https://docs.uptrain.ai/docs/uptrain-monitors/concept-drift)** - モデルのパフォーマンスをリアルタイムで追跡し、劣化アラートを取得します。
-   **[埋め込みのサポート](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)** - モデルによって推測された埋め込みを理解するための専用ダッシュボード。
-   **[エッジ ケース シグナル](https://docs.uptrain.ai/docs/uptrain-monitors/edge-case-detection)** - 分布外のデータポイントを検出するためのユーザー定義の信号と統計手法。
-   **[データ整合性チェック](https://docs.uptrain.ai/docs/uptrain-monitors/data-integrity)** - データの欠落または矛盾、重複レコード、データ品質などをチェックします。
-   **[カスタマイズ可能な指標](https://docs.uptrain.ai/docs/monitoring-custom-metrics)** - ユース ケースに適したカスタム メトリックを定義します。
-   **[自動再トレーニング](https://github.com/uptrain-ai/uptrain/blob/main/examples/human_orientation_classification/deepdive_examples/uptrain_check_all.ipynb)** - トレーニング パイプラインと推論パイプラインを接続して、モデルの再トレーニングを自動化します。
-   **[モデルバイアス](https://docs.uptrain.ai/docs/uptrain-monitors/model-bias)** - ML モデルの予測における偏りを追跡します。
-   **[AIの説明可能性](https://docs.uptrain.ai/docs/uptrain-visuals/shap-explainability)** - 予測における複数の機能の相対的な重要性を理解します。
-   **データセキュリティ** - あなたのデータはあなたのマシンの外に出ることはありません。
-   **Slack インテグレーション** - Slack でアラートを受け取ります。
-   **リアルタイム ダッシュボード** - モデルの健康状態をライブで視覚化します。

## 🚨近日公開🚨

-   **ラベル シフト** - 予測のドリフトを特定します。グラウンド トゥルースが利用できない場合に特に役立ちます。
-   **モデルの信頼区間** - モデル予測の信頼区間
-   **高度なドリフト検出技術** - 外れ値ベースのドリフト検出方法
-   **高度な機能スライス** - 統計プロパティをスライスする機能
-   **コルモゴロフ・スミルノフ検定** - 分布シフトの検出用
-   **予測の安定性** - モデル予測が安定していないケースをフィルタリングします。
-   **敵対的チェック** - 敵対的攻撃と戦う

もっと。


# 始めましょう🙌

すぐに始められます[Googleコラボはこちら](https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing%2F)。

マシンで実行するには、次の手順に従います。

### pip を使用してパッケージをインストールします。

```console
pip install uptrain
```

### 最初の例を実行します。

```console
git clone git@github.com:uptrain-ai/uptrain.git
cd uptrain/examples
pip install jupyterlab
jupyter lab
```

UpTrain の仕組みの簡単なチュートリアルについては、こちらをご覧ください[クイックスタート チュートリアル](https://docs.uptrain.ai/docs/uptrain-examples/quickstart-tutorial)。


# アップトレインイン[アクション](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)🎬

今日の ML の最も一般的な使用例の 1 つは言語モデルで、テキスト要約、NER、チャットボット、言語翻訳などがあります。UpTrain は、テキスト埋め込みの UMAP クラスタリング (推定バートから）。以下は、UpTrain ダッシュボードからのリプレイです。

### すぐに使える AI 説明可能性

<h1 align="left">
<img alt="umap_gif" width="60%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/ride_estimation/4_Explanability_recording.gif">
</h1>

### ライブ モデル パフォーマンス モニタリングとデータ整合性チェック

<h1 align="left">
<img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/fraud_detection/concept_drift_avg_acc.gif"> <img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/finetuning_llms/data_integrity.gif">
</h1>

### UMAP の次元削減と可視化

<h1 align="left">
<img alt="umap_gif" width="60%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/text_summarization/umap.gif">
</h1>

### 後でモデルを微調整するためのエッジ ケース コレクション

<h1 align="left">
<img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/finetuning_llms/edge_cases.gif">
</h1>

# アップトレインを選ぶ理由 🤔?

機械学習 (ML) モデルは、重要なビジネス上の意思決定を行うために広く使用されています。それでも、100% 正確な ML モデルはなく、さらに、時間の経過とともに精度が低下します😣.たとえば、消費者の購買習慣の変化により、売上予測は時間の経過とともに不正確になります。さらに、ML モデルのブラック ボックスの性質により、問題を特定して修正することは困難です。

UpTrain はこれを解決します。データ サイエンティストと ML エンジニアがモデルのどこに問題があるかを簡単に理解し、他の人が文句を言う前に修正​​できるようにします🗣️。

UpTrain は、LLM、推奨モデル、予測モデル、コンピューター ビジョン モデルなど、さまざまな機械学習モデルに使用できます。

私たちは、UpTrain をより良くするために常に取り組んでいます。新しい機能が必要ですか、または統合が必要ですか?お気軽に[問題を作成する](https://github.com/uptrain-ai/uptrain/issues)また[助ける](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md)リポジトリに直接。

<h1 align="center">
<img alt="Meme" width="40%" src="https://user-images.githubusercontent.com/108270398/215209245-4d6b1f47-7af9-4db8-8d8c-63dcc610571c.jpg">
</h1>

# ライセンス 💻

このリポジトリは、Apache 2.0 ライセンスの下で公開されています。私たちは現在、より多くの機能を追加し、より多くのモデルに拡張することで、ほとんどのユース ケースをカバーする非エンタープライズ サービスの開発に注力しています。また、ホステッド オファリングの追加に向けて取り組んでいます - [お問い合わせ](mailto:sourabh@insane.ai)もし興味があれば。

# 最新情報を入手☎️

私たちは、数多くの機能とユースケースを継続的に追加しています。プロジェクトに星を付けて、私たちをサポートしてください⭐!

# フィードバックを提供してください (厳しいほど良い 😉)

UpTrain を公開しています。フィードバックをお寄せいただき、改善にご協力ください **[ここ](https://forms.gle/PXd89D5LiFubro9o9)**。

# 貢献者 🖥️

アップトレインへの貢献を歓迎します。ご覧ください [貢献ガイド](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) 詳細については。

<a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=uptrain-ai/uptrain" />
</a>
