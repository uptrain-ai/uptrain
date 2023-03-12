<h4 align="center">
  <a href="https://uptrain.ai">
    <img width="300" src="https://user-images.githubusercontent.com/108270398/214240695-4f958b76-c993-4ddd-8de6-8668f4d0da84.png" alt="uptrain">
  </a>
</h4>
<h2>
  <p align="center">
    <p align="center">इंजीनियरों के लिए निर्मित एमएल अनुप्रयोगों का निरीक्षण करने के लिए एक ओपन-सोर्स फ्रेमवर्क</p>
  </p>
</h2>

<p align="center">
<a href="https://docs.uptrain.ai/docs/" rel="nofollow"><strong>
प्रलेखन</strong></a>
-
<a href="https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing/" rel="nofollow"><strong>प्रयोग करके देखो</strong></a>
-
<a href="https://discord.com/invite/gVvZhhrQaQ/" rel="nofollow"><strong>समर्थन समुदाय</strong></a>
-
<a href="https://github.com/uptrain-ai/uptrain/issues/new?assignees=&labels=bug&template=bug_report.md&title=" rel="nofollow"><strong>बग रिपोर्ट</strong></a>
-
<a href="https://github.com/uptrain-ai/uptrain/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=" rel="nofollow"><strong>सुविधा का अनुरोध</strong></a>
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

**इसे अन्य भाषाओं में पढ़ें**: 
<kbd>[<img title="English" alt="English language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/us.svg" width="22">](/README.md)</kbd>
<kbd>[<img title="German" alt="German language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/de.svg" width="22">](/i18n/README.de.md)</kbd>
<kbd>[<img title="Chinese" alt="Chinese language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/cn.svg" width="22">](/i18n/README.zh-CN.md)</kbd>
<kbd>[<img title="Hindi" alt="Hindi language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/in.svg" width="22">](/i18n/README.hi.md)</kbd>
<kbd>[<img title="Spanish" alt="Spanish language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/es.svg" width="22">](/i18n/README.es.md)</kbd>
<kbd>[<img title="French" alt="French language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/fr.svg" width="22">](/i18n/README.fr.md)</kbd>
<kbd>[<img title="Japanese" alt="Japanese language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/jp.svg" width="22">](/i18n/README.ja.md)</kbd>
<kbd>[<img title="Russian" alt="Russian language" src="https://cdn.staticaly.com/gh/hjnilsson/country-flags/master/svg/ru.svg" width="22">](/i18n/README.ru.md)</kbd>


**[UpTrain](https://uptrain.ai)** एमएल प्रैक्टिशनर्स के लिए एक ओपन-सोर्स, डेटा-सिक्योर टूल है, जो उनके प्रदर्शन की निगरानी करके, (डेटा) डिस्ट्रीब्यूशन शिफ्ट्स की जांच करके और उन्हें फिर से प्रशिक्षित करने के लिए एज केस इकट्ठा करके उनके एमएल मॉडल का निरीक्षण और परिशोधन करता है। यह आपकी मौजूदा उत्पादन पाइपलाइनों के साथ मूल रूप से एकीकृत होता है और आरंभ करने में कुछ मिनट लेता है।

# **[प्रमुख विशेषताऐं](https://uptrain.gitbook.io/docs/what-is-uptrain/key-features)** 💡

-   **[डेटा बहाव चेक](https://docs.uptrain.ai/docs/uptrain-monitors/data-drift)** - अपने मॉडल इनपुट में वितरण बदलाव की पहचान करें।
-   **[निष्पादन की निगरानी](https://docs.uptrain.ai/docs/uptrain-monitors/concept-drift)** - वास्तविक समय में अपने मॉडलों के प्रदर्शन को ट्रैक करें और गिरावट अलर्ट प्राप्त करें।
-   **[एम्बेडिंग समर्थन](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)** - मॉडल-अनुमानित एम्बेडिंग को समझने के लिए विशिष्ट डैशबोर्ड।
-   **[एज केस सिग्नल](https://docs.uptrain.ai/docs/uptrain-monitors/edge-case-detection)** - आउट-ऑफ़-डिस्ट्रीब्यूशन डेटा-पॉइंट्स का पता लगाने के लिए उपयोगकर्ता-परिभाषित सिग्नल और सांख्यिकीय तकनीकें।
-   **[डेटा अखंडता जाँच](https://docs.uptrain.ai/docs/uptrain-monitors/data-integrity)** - अनुपलब्ध या असंगत डेटा, डुप्लिकेट रिकॉर्ड, डेटा गुणवत्ता आदि की जाँच करता है।
-   **[अनुकूलन मेट्रिक्स](https://docs.uptrain.ai/docs/monitoring-custom-metrics)** - कस्टम मेट्रिक्स को परिभाषित करें जो आपके उपयोग के मामले के लिए मायने रखता है।
-   **[स्वचालित पुनर्प्रशिक्षण](https://github.com/uptrain-ai/uptrain/blob/main/examples/human_orientation_classification/deepdive_examples/uptrain_check_all.ipynb)** - अपने प्रशिक्षण और अनुमान पाइपलाइनों को जोड़कर मॉडल को स्वचालित करें।
-   **[मॉडल पूर्वाग्रह](https://docs.uptrain.ai/docs/uptrain-monitors/model-bias)** - अपने एमएल मॉडल की भविष्यवाणियों में पक्षपात को ट्रैक करें।
-   **[AI Explainability](https://docs.uptrain.ai/docs/uptrain-visuals/shap-explainability)** - भविष्यवाणियों पर कई विशेषताओं के सापेक्ष महत्व को समझें।
-   **डाटा सुरक्षा** - आपका डेटा आपकी मशीन से कभी बाहर नहीं जाता है।
-   **सुस्त एकीकरण** - स्लैक पर अलर्ट प्राप्त करें।
-   **रीयलटाइम डैशबोर्ड** - अपने मॉडल के स्वास्थ्य की लाइव कल्पना करने के लिए।

## 🚨जल्द आ रहा है🚨

-   **लेबल शिफ्ट** - अपनी भविष्यवाणियों में बहाव की पहचान करें। उन मामलों में विशेष रूप से उपयोगी जब जमीनी सच्चाई अनुपलब्ध हो।
-   **मॉडल विश्वास अंतराल** - मॉडल भविष्यवाणियों के लिए विश्वास अंतराल
-   **उन्नत बहाव पहचान तकनीक** - बाहरी-आधारित बहाव का पता लगाने के तरीके
-   **उन्नत सुविधा टुकड़ा करने की क्रिया** - सांख्यिकीय गुणों को टुकड़ा करने की क्षमता
-   **कोलमोगोरोव-स्मिर्नोव परीक्षण** - वितरण पारियों का पता लगाने के लिए
-   **भविष्यवाणी स्थिरता** - फ़िल्टर मामले जहां मॉडल भविष्यवाणी स्थिर नहीं है।
-   **प्रतिकूल चेक** - प्रतिकूल हमलों का मुकाबला करें

और अधिक।


# शुरू करें 🙌

आप जल्दी से शुरू कर सकते हैं [गूगल कोलाब यहाँ](https://colab.research.google.com/drive/1ZIITMB7XYotvhg5CNvGPFnBdM4SR2w4Q?usp=sharing%2F).

इसे अपनी मशीन में चलाने के लिए, नीचे दिए गए चरणों का पालन करें:

### पिप के माध्यम से पैकेज स्थापित करें:

```console
pip install uptrain
```

### अपना पहला उदाहरण चलाएँ:

```console
git clone git@github.com:uptrain-ai/uptrain.git
cd uptrain/examples
pip install jupyterlab
jupyter lab
```

UpTrain कैसे काम करता है, इस बारे में त्वरित जानकारी के लिए, हमारा देखें [त्वरित प्रारंभ ट्यूटोरियल](https://docs.uptrain.ai/docs/uptrain-examples/quickstart-tutorial).


# UpTrain में [कार्य](https://github.com/uptrain-ai/uptrain/blob/main/examples/text_summarization/run.ipynb)🎬

एमएल के सबसे आम उपयोग मामलों में से एक आज भाषा मॉडल है, चाहे वह टेक्स्ट सारांश, एनईआर, चैटबॉट, भाषा अनुवाद इत्यादि हो। बर्ट से)। UpTrain डैशबोर्ड से कुछ रिप्ले निम्नलिखित हैं।

### एआई व्याख्यात्मकता आउट-ऑफ़-द-बॉक्स

<h1 align="left">
<img alt="umap_gif" width="60%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/ride_estimation/4_Explanability_recording.gif">
</h1>

### लाइव मॉडल प्रदर्शन निगरानी और डेटा अखंडता जांच

<h1 align="left">
<img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/fraud_detection/concept_drift_avg_acc.gif"> <img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/finetuning_llms/data_integrity.gif">
</h1>

### यूएमएपी आयाम में कमी और विज़ुअलाइज़ेशन

<h1 align="left">
<img alt="umap_gif" width="60%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/text_summarization/umap.gif">
</h1>

### मॉडल को बाद में फ़ाइनट्यूनिंग के लिए एज-केस संग्रह

<h1 align="left">
<img alt="perf_gif" width="40%" src="https://uptrain-demo.s3.us-west-1.amazonaws.com/finetuning_llms/edge_cases.gif">
</h1>

# UpTrain क्यों 🤔?

महत्वपूर्ण व्यावसायिक निर्णय लेने के लिए मशीन लर्निंग (एमएल) मॉडल का व्यापक रूप से उपयोग किया जाता है। फिर भी, कोई एमएल मॉडल 100% सटीक नहीं है, और आगे, उनकी सटीकता समय के साथ बिगड़ती जाती है 😣। उदाहरण के लिए, उपभोक्ता की खरीदारी की आदतों में बदलाव के कारण बिक्री की भविष्यवाणी समय के साथ गलत हो जाती है। इसके अतिरिक्त, एमएल मॉडल की ब्लैक बॉक्स प्रकृति के कारण, उनकी समस्याओं की पहचान करना और उन्हें ठीक करना चुनौतीपूर्ण है।

UpTrain इसे हल करती है। हम डेटा वैज्ञानिकों और एमएल इंजीनियरों के लिए यह समझना आसान बनाते हैं कि उनके मॉडल कहां गलत हो रहे हैं और दूसरों की शिकायत 🗣️ से पहले उन्हें ठीक करने में उनकी मदद करते हैं।

UpTrain का उपयोग विभिन्न प्रकार के मशीन लर्निंग मॉडल जैसे LLM, अनुशंसा मॉडल, भविष्यवाणी मॉडल, कंप्यूटर विज़न मॉडल आदि के लिए किया जा सकता है।

हम UpTrain को बेहतर बनाने के लिए लगातार काम कर रहे हैं। कोई नई सुविधा चाहते हैं या किसी एकीकरण की आवश्यकता है? करने के लिए स्वतंत्र महसूस [एक मुद्दा बनाएँ](https://github.com/uptrain-ai/uptrain/issues) या [योगदान देना](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) सीधे रिपॉजिटरी में।

<h1 align="center">
<img alt="Meme" width="40%" src="https://user-images.githubusercontent.com/108270398/215209245-4d6b1f47-7af9-4db8-8d8c-63dcc610571c.jpg">
</h1>

# लाइसेंस 💻

यह रेपो Apache 2.0 लाइसेंस के तहत प्रकाशित किया गया है। हम वर्तमान में गैर-उद्यम पेशकशों को विकसित करने पर ध्यान केंद्रित कर रहे हैं जो अधिक सुविधाओं को जोड़कर और अधिक मॉडलों को विस्तारित करके अधिकांश उपयोग मामलों को कवर करें। हम एक होस्टेड पेशकश को जोड़ने की दिशा में भी काम कर रहे हैं - [संपर्क करें](mailto:sourabh@insane.ai) अगर आपको रुचि हो तो।

# अपडेट रहें ☎️

हम लगातार ढेर सारी सुविधाएं और उपयोग के मामले जोड़ रहे हैं। कृपया प्रोजेक्ट को एक स्टार ⭐ देकर हमारा समर्थन करें!

# प्रतिक्रिया दें (कठोर बेहतर 😉)

हम सार्वजनिक रूप से UpTrain का निर्माण कर रहे हैं। अपनी प्रतिक्रिया देकर हमें बेहतर बनाने में मदद करें **[यहाँ](https://forms.gle/PXd89D5LiFubro9o9)**.

# योगदानकर्ता 🖥️

हम UpTrain में योगदान का स्वागत करते हैं। कृपया हमारे देखें [योगदान गाइड](https://github.com/uptrain-ai/uptrain/blob/main/CONTRIBUTING.md) अधिक जानकारी के लिए।

<a href="https://github.com/uptrain-ai/uptrain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=uptrain-ai/uptrain" />
</a>
