import ButtonSection from "@/components/Common/ButtonSection";
import CloseButtonSection from "@/components/Common/CloseButtonSection";
import ChartSection from "@/components/Evaluations/ChartPage/ChartSection";
import TableSection from "@/components/Evaluations/ChartPage/Logs_InsightsTable";
import Header from "@/components/Header";
import SpinningLoader from "@/components/UI/SpinningLoader";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import React, { useLayoutEffect, useState } from "react";
import { useSelector } from "react-redux";
import Row from "../Row";

const fetchEvaluationData = async (
  uptrainAccessKey,
  evaluationId,
  setEvaluationData
) => {
  try {
    const response = await fetch(
      process.env.NEXT_PUBLIC_BACKEND_URL +
        `api/public/get_data?evaluation_id=${evaluationId}`,
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

      setEvaluationData(responseData.data);
    } else {
      console.error("Failed to submit API Key:", response.statusText);
      // Handle error cases
    }
  } catch (error) {
    console.error("Error submitting API Key:", error.message);
    // Handle network errors or other exceptions
  }
};

const EvaluationModal = (props) => {
  const [evaluationData, setEvaluationData] = useState(null);
  const [Tab, setTab] = useState(0);

  const tabs = evaluationData && evaluationData[2];
  const selectedTab = tabs && tabs[Tab];

  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  useLayoutEffect(() => {
    const fetchDataAsync = async () => {
      await fetchEvaluationData(
        uptrainAccessKey,
        props.evaluationId,
        setEvaluationData
      );
    };

    if (uptrainAccessKey && props.evaluationId) {
      fetchDataAsync();
    }
  }, [uptrainAccessKey, props.evaluationId]);

  var filteredData = evaluationData;

  return (
    <div
      className="fixed top-0 left-0 w-screen h-screen backdrop-blur flex items-center justify-center overflow-auto p-10 z-10"
      onClick={props.onClick}
    >
      <div
        className="rounded-xl border-[#5587FD] border bg-[#0E0E13] p-8 max-w-[80%] w-full max-h-[100%] overflow-auto"
        onClick={(event) => {
          // This will stop the event from bubbling up the DOM tree
          event.stopPropagation();
          // Your click handling logic here
        }}
      >
        <CloseButtonSection onClick={props.onClick} />
        <div className="flex-1 flex flex-col">
          {evaluationData ? (
            <div className="flex-1">
              <Header
                heading={props.heading}
                project={props.project}
                className="my-0"
              />
              <div className="bg-[#23232D] rounded-xl p-8 mb-5">
                <Row data={props.data} />
              </div>
              <ButtonSection
                tabs={tabs}
                Tab={Tab}
                setTab={setTab}
                checks={evaluationData[3].checks}
                prompt
              />
              <ChartSection
                projectData={filteredData}
                selectedTab={selectedTab}
              />
              <TableSection
                projectData={filteredData}
                selectedTab={selectedTab}
              />
            </div>
          ) : (
            <div className="flex justify-center items-center h-screen">
              <SpinningLoader />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EvaluationModal;
