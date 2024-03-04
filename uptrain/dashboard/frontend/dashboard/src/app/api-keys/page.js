"use client";
import CodeViewer from "@/components/ApiKeys/CodeViewer";
import Layout from "@/components/Layout";
import GrayParah18 from "@/components/UI/GrayParah18";
import GraySmallHeading from "@/components/UI/GraySmallHeading";
import {
  selectTotalCredits,
  selectUptrainAccessKey,
  selectUsedCredits,
} from "@/store/reducers/userInfo";
import Image from "next/image";
import React, { useState } from "react";
import { useSelector } from "react-redux";

const Working = (props) => {
  return (
    <div className="bg-[#171721] w-full p-3 rounded-xl mt-1.5">
      {props.children}
    </div>
  );
};

const ApiSection = () => {
  const uptrainAccessKey = useSelector(selectUptrainAccessKey);
  const copyToClipboard = () => {
    navigator.clipboard.writeText(uptrainAccessKey);
  };

  return (
    <div className="mb-8">
      <GraySmallHeading>Your API Key</GraySmallHeading>
      <div className="gap-3 flex items-center">
        <div className="bg-[#171721] rounded-xl flex justify-between py-2.5 px-5 items-center mt-1.5 flex-1">
          <GrayParah18>{uptrainAccessKey}</GrayParah18>
          <button onClick={copyToClipboard}>
            <Image src="./CopyIcon.svg" width={18} height={18} />
          </button>
        </div>
        {/* <button className="bg-transparent border-[#5587FD] border-2 rounded-xl px-5 py-3 font-medium text-sm text-[#5587FD] hover:bg-[#5587FD] hover:text-[#171721]">
          Revoke API Key
        </button> */}
      </div>
    </div>
  );
};

const CreditsSection = () => {
  const totalCredits = useSelector(selectTotalCredits);
  const usedCredits = useSelector(selectUsedCredits);

  return (
    <div className="mb-8">
      <GraySmallHeading>Credits left</GraySmallHeading>
      <GrayParah18 className="mt-1.5">
        {usedCredits}
        <span className="text-[#4F4F56]">/{totalCredits}</span>
      </GrayParah18>
    </div>
  );
};

const TabButton = (props) => {
  return (
    <button
      className={`font-medium border-b-2 px-3 pb-1  ${
        props.selected
          ? "text-[#F0F0F8] border-[#5587FD]"
          : "text-[#5C5C66] border-[#5C5C66]"
      }`}
      onClick={props.onClick}
    >
      <p>{props.title}</p>
    </button>
  );
};

const ButtonSection = (props) => {
  return (
    <div className="flex justify-between mb-5">
      <div className="flex gap-5">
        <TabButton
          selected={props.tabs == 0}
          onClick={() => {
            props.setTabs(0);
          }}
          title="Log and Evaluate"
        />
        <TabButton
          selected={props.tabs == 1}
          onClick={() => {
            props.setTabs(1);
          }}
          title="Experiments"
        />
        <TabButton
          selected={props.tabs == 2}
          onClick={() => {
            props.setTabs(2);
          }}
          title="Open Source"
        />
      </div>
      <button onClick={props.onClick}>
        <Image src="/CopyIcon.svg" width={24} height={24} alt="copy icon" />
      </button>
    </div>
  );
};

const WorkingSection = () => {
  const [tabs, setTabs] = useState(0);
  const apiKey = useSelector(selectUptrainAccessKey);

  const openSource = `from uptrain import EvalLLM, Evals, CritiqueTone
import json

OPENAI_API_KEY = "sk-***************"

data = [{
    'question': 'Which is the most popular global sport?',
    'context': "The popularity of sports can be measured in various ways, including TV viewership, social media presence, number of participants, and economic impact. Football is undoubtedly the world's most popular sport with major events like the FIFA World Cup and sports personalities like Ronaldo and Messi, drawing a followership of more than 4 billion people. ",
    'response': 'Football is the most popular sport with around 4 billion followers worldwide'
}]

eval_llm = EvalLLM(openai_api_key=OPENAI_API_KEY)

results = eval_llm.evaluate(
    data=data,
    checks=[Evals.CONTEXT_RELEVANCE, Evals.FACTUAL_ACCURACY, Evals.RESPONSE_RELEVANCE, CritiqueTone(persona="teacher")]
)

print(json.dumps(results, indent=3))`;

  const experiments = `from uptrain import APIClient, Evals, CritiqueTone
import json

UPTRAIN_API_KEY = "${
    apiKey == undefined || apiKey == "None" ? "up-***************" : apiKey
  }"

data = [{
    "question": "How can you ensure that a designed prompt elicits the desired response from a language model?",
    "context": "nudge the model to generate a desired result. Prompt design can be an efficient way to experiment with adapting a language model for a specific use case.",
    "response": "To ensure that a designed prompt elicits the desired response from a language model, you can experiment with different prompt designs that nudge the model towards generating the desired result. This can be an efficient way to adapt the language model for a specific use case.",
    "chunk_size": 200
},
{
    "question": "How can you ensure that a designed prompt elicits the desired response from a language model?",
    "context": "Design and save your own promptsPrompt design is the process of manually creating prompts that elicit the desired response from a language model. By carefully crafting prompts, you can nudge the model to generate a desired result. Prompt design can be an efficient way to experiment with adapting a language model for a specific use case. You can create and save your own prompts in Vertex AI Studio. When creating a new prompt, you enter the prompt text, specify the model to use, configure parameter values, and test the prompt by generating a response. You can iterate on the prompt and its configurations until you get the desired results. When you are done designing the prompt, you can save it in Vertex AI Studio. Response citations If you are using a text model in Vertex AI Studio like text-bison, you receive text responses based on your input. Our features are intended to produce original content and not replicate existing content at length. If",
    "response": "To ensure that a designed prompt elicits the desired response from a language model, you can manually create prompts that carefully craft the desired result. By iterating on the prompt and its configurations in Vertex AI Studio, you can experiment and adjust until you achieve the desired results. Additionally, it is important to note that the text models in Vertex AI Studio are designed to produce original content and not replicate existing content at length.",
    "chunk_size": 1000
}]

client = APIClient(uptrain_api_key=UPTRAIN_API_KEY)

results = client.evaluate_experiments(
    project_name="Chunk-Size-Experiment",
    data=data,
    checks=[Evals.CONTEXT_RELEVANCE, Evals.RESPONSE_RELEVANCE, Evals.FACTUAL_ACCURACY],
    exp_columns=["chunk_size"]
)

print(json.dumps(results, indent=3))`;

  const log = `from uptrain import APIClient, Evals, CritiqueTone
import json

UPTRAIN_API_KEY = "${
    apiKey == undefined || apiKey == "None" ? "up-***************" : apiKey
  }"

data = [{
    'question': 'Which is the most popular global sport?',
    'context': "The popularity of sports can be measured in various ways, including TV viewership, social media presence, number of participants, and economic impact. Football is undoubtedly the world's most popular sport with major events like the FIFA World Cup and sports personalities like Ronaldo and Messi, drawing a followership of more than 4 billion people. ",
    'response': 'Football is the most popular sport with around 4 billion followers worldwide'
}]

client = APIClient(uptrain_api_key=UPTRAIN_API_KEY)

results = client.log_and_evaluate(
    project_name="Sample-Project",
    data=data,
    checks=[Evals.CONTEXT_RELEVANCE, Evals.FACTUAL_ACCURACY, Evals.RESPONSE_RELEVANCE, CritiqueTone(persona="teacher")]
)

print(json.dumps(results, indent=3))`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(
      tabs === 0 ? log : tabs === 1 ? experiments : openSource
    );
  };

  return (
    <div className="mb-8">
      <GraySmallHeading>How it Works</GraySmallHeading>
      <Working>
        <ButtonSection
          tabs={tabs}
          setTabs={setTabs}
          onClick={copyToClipboard}
        />
        <pre className="overflow-auto">
          {tabs === 0 ? (
            <CodeViewer horizontal>{log}</CodeViewer>
          ) : tabs === 1 ? (
            <CodeViewer horizontal>{experiments}</CodeViewer>
          ) : (
            <CodeViewer horizontal>{openSource}</CodeViewer>
          )}
        </pre>
      </Working>
    </div>
  );
};

const page = () => {
  return (
    <Layout heading="API Keys">
      <div className="bg-[#23232D] rounded-xl p-8 w-[calc(100vw-640px)]">
        {/* <ApiSection />
        <CreditsSection /> */}
        <WorkingSection />
      </div>
    </Layout>
  );
};

export default page;
