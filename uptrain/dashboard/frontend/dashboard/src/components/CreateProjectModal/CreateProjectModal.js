import React, { useState } from "react";
import { useSelector } from "react-redux";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import SpinningLoader from "../UI/SpinningLoader";
import CloseButtonSection from "./CloseButtonSection";
import Step1 from "./Step1";
import Step2 from "./Step2";
import Step3 from "./Step3";

const CreateProjectModal = (props) => {
  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  const [step, setStep] = useState(1);
  const [projectName, setProjectName] = useState("");
  const [datasetName, setDatasetName] = useState("");
  const [selectedOption, setSelectedOption] = useState("");
  const [selectedProjectType, setSelectedProjectType] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedChecks, setselectedChecks] = useState([]);
  const [selectedMultiChecks, setSelectedMultiChecks] = useState([]);
  const [promptName, setPromptName] = useState("");
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [metadata, setMetadata] = useState({});

  const singleMetrics = [
    "context_relevance",
    "factual_accuracy",
    "response_relevance",
    "critique_language",
    "response_completeness",
    "response_completeness_wrt_context",
    "response_consistency",
    "response_conciseness",
    "valid_response",
    "response_alignment_with_scenario",
    "response_sincerity_with_scenario",
    "prompt_injection",
    "code_hallucination",
    "sub_query_completeness",
    "context_reranking",
    "context_conciseness",
  ];

  const multiMetrics = {
    GuidelineAdherence: ["guideline"],
    CritiqueTone: ["llm_persona"],
    ResponseMatching: ["method"],
    JailbreakDetection: ["model_purpose"],
    ConversationSatisfaction: ["user_persona", "llm_persona"],
  };

  const models = {
    "gpt-3.5-turbo": ["openai_api_key"],
    "gpt-4": ["openai_api_key"],
    "gpt-4-turbo-preview": ["openai_api_key"],
    "claude-2.1": ["anthropic_api_key"],
    "azure-deployment": [
      "azure_api_base",
      "azure_api_version",
      "azure_api_key",
    ],
  };

  const handleEvaluationSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);

    console.log(metadata);

    try {
      const formData = new FormData();
      formData.append("model", selectedOption);
      formData.append("project_name", projectName);
      formData.append(
        "checks",
        JSON.stringify(
          singleMetrics
            .filter((item, index) => selectedChecks.includes(index))
            .concat(selectedMultiChecks)
        )
      );
      formData.append("dataset_name", datasetName);
      formData.append("data_file", selectedFile);
      formData.append("metadata", JSON.stringify(metadata));

      const response = await fetch(
        process.env.NEXT_PUBLIC_BACKEND_URL + `api/public/add_evaluation`,
        {
          method: "POST",
          headers: {
            "uptrain-access-token": `${uptrainAccessKey}`,
          },
          body: formData,
        }
      );

      if (response.ok) {
        props.reloadData();
        setLoading(false);
        props.close();
        const responseData = await response.json();
      } else {
        console.error("Failed to submit:", response.statusText);
        // Handle error cases
      }
    } catch (error) {
      console.error("Error submitting:", error.message);
      // Handle network errors or other exceptions
    }
  };

  const handlePromptSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("model", selectedOption);
      formData.append(
        "project_name",
        props.promptProjectName ? props.promptProjectName : projectName
      );
      formData.append(
        "checks",
        JSON.stringify(
          singleMetrics
            .filter((item, index) => selectedChecks.includes(index))
            .concat(selectedMultiChecks)
        )
      );
      formData.append("dataset_name", datasetName);
      formData.append("data_file", selectedFile);
      formData.append("prompt", prompt);
      formData.append(
        "prompt_name",
        props.promptVersionName ? props.promptVersionName : promptName
      );
      formData.append("metadata", JSON.stringify(metadata));

      const response = await fetch(
        process.env.NEXT_PUBLIC_BACKEND_URL + `api/public/add_prompts`,
        {
          method: "POST",
          headers: {
            "uptrain-access-token": `${uptrainAccessKey}`,
          },
          body: formData,
        }
      );

      if (response.ok) {
        const responseData = await response.json();
        props.reloadData();
        setLoading(false);
        props.close();
      } else {
        console.error("Failed to submit:", response.statusText);
        // Handle error cases
      }
    } catch (error) {
      console.error("Error submitting:", error.message);
      // Handle network errors or other exceptions
    }
  };

  return (
    <div className="fixed top-0 left-0 w-screen h-screen backdrop-blur flex items-center justify-center overflow-auto p-10 z-20">
      <div className="rounded-xl border-[#5587FD] bg-[#23232D] p-8 max-w-[70%] w-full max-h-[100%] overflow-auto">
        <CloseButtonSection onClick={props.close} />
        {loading ? (
          <div class="flex justify-center items-center flex-col h-[60vh]">
            <SpinningLoader />
            <p className="mt-2 text-lg text-white font-medium">
              Please wait while we process your data
            </p>
          </div>
        ) : step === 1 ? (
          <Step1
            models={models}
            nextEvaluation={() => setStep(3)}
            nextPrompt={() => setStep(2)}
            setProjectName={setProjectName}
            setSelectedProjectType={setSelectedProjectType}
            selectedProjectType={selectedProjectType}
            projectName={projectName}
            datasetName={datasetName}
            setDatasetName={setDatasetName}
            selectedOption={selectedOption}
            setSelectedOption={setSelectedOption}
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
            promptProjectName={props.promptProjectName}
            metadata={metadata}
            setMetadata={setMetadata}
          />
        ) : step === 2 ? (
          <Step2
            next={() => setStep(3)}
            promptName={promptName}
            setPromptName={setPromptName}
            prompt={prompt}
            setPrompt={setPrompt}
            promptVersionName={props.promptVersionName}
          />
        ) : (
          <Step3
            next={
              selectedProjectType === "Evaluation"
                ? handleEvaluationSubmit
                : handlePromptSubmit
            }
            singleMetrics={singleMetrics}
            multiMetrics={multiMetrics}
            selectedChecks={selectedChecks}
            setselectedChecks={setselectedChecks}
            selectedMultiChecks={selectedMultiChecks}
            setSelectedMultiChecks={setSelectedMultiChecks}
            metadata={metadata}
            setMetadata={setMetadata}
          />
        )}
      </div>
    </div>
  );
};

export default CreateProjectModal;
