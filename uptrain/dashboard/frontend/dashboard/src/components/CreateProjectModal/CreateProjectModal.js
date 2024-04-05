import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import SpinningLoader from "../UI/SpinningLoader";
import CloseButtonSection from "../Common/CloseButtonSection";
import Step1 from "./Step1";
import { models } from "@/utils/models";
import Step2 from "../Common/Step2";

const CreateProjectModal = (props) => {
  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  const [step, setStep] = useState(1);
  const [projectName, setProjectName] = useState("");
  const [datasetName, setDatasetName] = useState("");
  const [selectedOption, setSelectedOption] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedChecks, setselectedChecks] = useState([]);
  const [selectedMultiChecks, setSelectedMultiChecks] = useState([]);
  const [metadata, setMetadata] = useState({});
  const [loading, setLoading] = useState(false);

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

  const handleProjectSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);

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
        process.env.NEXT_PUBLIC_BACKEND_URL + `api/public/create_project`,
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

  return (
    <div className="fixed top-0 left-0 w-screen h-screen backdrop-blur flex items-center justify-center overflow-auto p-10 z-20">
      <div className="rounded-xl border-[#5587FD] bg-[#23232D] p-8 max-w-[70%] w-full max-h-[100%] overflow-auto">
        <CloseButtonSection onClick={props.close} />
        {loading ? (
          <div className="flex justify-center items-center flex-col h-[60vh]">
            <SpinningLoader />
            <p className="mt-2 text-lg text-white font-medium">
              Please wait while we process your data
            </p>
          </div>
        ) : step === 1 ? (
          <Step1
            models={models}
            next={() => setStep(2)}
            setProjectName={setProjectName}
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
            projectNames={props.projectNames}
          />
        ) : (
          <Step2
            next={handleProjectSubmit}
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
