import CloseButtonSection from "@/components/Common/CloseButtonSection";
import React, { useLayoutEffect, useState } from "react";
import Step1 from "./Step1";
import SpinningLoader from "@/components/UI/SpinningLoader";
import { useSelector } from "react-redux";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import Step2 from "@/components/Common/Step2";
import { models } from "@/utils/models";

const fetchDatasetData = async (
  uptrainAccessKey,
  projectId,
  setDatasetData
) => {
  try {
    const response = await fetch(
      process.env.NEXT_PUBLIC_BACKEND_URL +
        `api/public/project_datasets?project_id=${projectId}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "uptrain-access-token": `${uptrainAccessKey}`,
        },
      }
    );

    if (response.ok) {
      const responseData = await response.json();

      setDatasetData(responseData);
    } else {
      console.error("Failed to submit API Key:", response.statusText);
      // Handle error cases
    }
  } catch (error) {
    console.error("Error submitting API Key:", error.message);
    // Handle network errors or other exceptions
  }
};

const AddProjectModal = (props) => {
  const [step, setStep] = useState(1);
  const [selectedChecks, setSelectedChecks] = useState([]);
  const [selectedMultiChecks, setSelectedMultiChecks] = useState([]);
  const [metadata, setMetadata] = useState({});
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedOption, setSelectedOption] = useState("");
  const [loading, setLoading] = useState(false);
  const [evaluationName, setEvaluationName] = useState("");
  const [datasetData, setDatasetData] = useState([]);
  const [dataset, setSelectedDataset] = useState(null);
  const [datasetName, setDatasetName] = useState("");

  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  const dataSetOptions = datasetData.map(
    (item) => item.name + " V" + item.version
  );

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

  useLayoutEffect(() => {
    const fetchDataAsync = async () => {
      await fetchDatasetData(uptrainAccessKey, props.projectId, setDatasetData);
    };

    if (uptrainAccessKey && props.projectId) {
      fetchDataAsync();
    }
  }, [uptrainAccessKey, props.projectId]);

  useLayoutEffect(() => {
    const singleChecks = [];
    const multiChecks = [];
    const data = {};

    for (let i = 0; i < props.checks.checks.length; i++) {
      const item = props.checks.checks[i];
      if (singleMetrics.includes(item.check_name)) {
        singleChecks.push(singleMetrics.indexOf(item.check_name));
      } else if (multiMetrics.hasOwnProperty(item.check_name)) {
        multiChecks.push(item.check_name);
        data[item.check_name] = {};

        for (const key in item) {
          if (key === "check_name") continue;
          data[item.check_name][key] = item[key];
        }
      }
    }

    setSelectedChecks(singleChecks);
    setSelectedMultiChecks(multiChecks);
    setMetadata(data);
  }, []);

  const handleProjectSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);

    try {
      const data = {
        model: selectedOption,
        checks: singleMetrics
          .filter((item, index) => selectedChecks.includes(index))
          .concat(selectedMultiChecks),
        project_id: props.projectId,
        dataset_id: datasetData[dataset].id,
        metadata: metadata,
        evaluation_name: evaluationName,
      };

      const response = await fetch(
        process.env.NEXT_PUBLIC_BACKEND_URL + `api/public/add_default_run`,
        {
          method: "POST",
          headers: {
            "uptrain-access-token": `${uptrainAccessKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
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

  const handleNewDataProjectSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("model", selectedOption);
      formData.append("project_id", props.projectId);
      formData.append(
        "checks",
        JSON.stringify(
          singleMetrics
            .filter((item, index) => selectedChecks.includes(index))
            .concat(selectedMultiChecks)
        )
      );
      formData.append("evaluation_name", evaluationName);
      formData.append("data_file", selectedFile);
      formData.append("metadata", JSON.stringify(metadata));
      formData.append("dataset_name", datasetName);

      const response = await fetch(
        process.env.NEXT_PUBLIC_BACKEND_URL + `api/public/new_run`,
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
        ) : step == 1 ? (
          <Step1
            databaseId={props.databaseId}
            next={() => setStep(2)}
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
            models={models}
            setSelectedOption={setSelectedOption}
            selectedOption={selectedOption}
            evaluationName={evaluationName}
            setEvaluationName={setEvaluationName}
            projectData={props.projectData}
            dataSetOptions={dataSetOptions}
            dataset={dataset}
            setSelectedDataset={setSelectedDataset}
            datasetName={datasetName}
            setDatasetName={setDatasetName}
            metadata={metadata}
            setMetadata={setMetadata}
          />
        ) : (
          step == 2 && (
            <Step2
              next={
                selectedFile ? handleNewDataProjectSubmit : handleProjectSubmit
              }
              databaseId={props.databaseId}
              singleMetrics={singleMetrics}
              multiMetrics={multiMetrics}
              selectedChecks={selectedChecks}
              setselectedChecks={setSelectedChecks}
              selectedMultiChecks={selectedMultiChecks}
              setSelectedMultiChecks={setSelectedMultiChecks}
              metadata={metadata}
              setMetadata={setMetadata}
            />
          )
        )}
      </div>
    </div>
  );
};

export default AddProjectModal;
