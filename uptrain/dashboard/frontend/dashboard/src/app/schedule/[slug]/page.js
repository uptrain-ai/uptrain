"use client";
import ButtonSection from "@/components/Common/ButtonSection";
import ChartSection from "@/components/OldEvaluations/ChartSection";
import TableSection from "@/components/OldEvaluations/Logs_InsightsTable";
import Layout from "@/components/Layout";
import SpinningLoader from "@/components/UI/SpinningLoader";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import { useRouter } from "next/navigation";
import React, { useLayoutEffect, useState } from "react";
import { useSelector } from "react-redux";

const fetchEvaluationData = async (
  uptrainAccessKey,
  projectId,
  setEvaluationData,
  router
) => {
  try {
    const response = await fetch(
      process.env.NEXT_PUBLIC_BACKEND_URL +
        `api/public/get_project_data?project_id=${projectId}&project_type=schedule`,
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

const page = ({ params: { slug } }) => {
  const router = useRouter();

  const [evaluationData, setEvaluationData] = useState(null);
  const [Tab, setTab] = useState(0);
  const [projectFilters, setProjectFilters] = useState({});

  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  const tabs = evaluationData && evaluationData[3];
  const selectedTab = tabs && tabs[Tab];

  useLayoutEffect(() => {
    const fetchDataAsync = async () => {
      await fetchEvaluationData(
        uptrainAccessKey,
        slug,
        setEvaluationData,
        router
      );
    };

    if (uptrainAccessKey) {
      fetchDataAsync();
    }
  }, [uptrainAccessKey]);

  let filteredData = JSON.parse(JSON.stringify(evaluationData));

  if (filteredData) {
    filteredData[0] = filteredData[0].map((item, index) => {
      item.id = index; // Assuming 'id' is the field you want to update
      return item;
    });
  }

  if (filteredData && projectFilters.hasOwnProperty("index")) {
    filteredData[0] = filteredData[0].filter(
      (item, index) => !projectFilters["index"].includes(index + 1)
    );
  }

  if (filteredData && projectFilters.hasOwnProperty("scores")) {
    filteredData[0] = filteredData[0].filter((item, index) => {
      return !projectFilters["scores"].includes(
        item["checks"][`score_${selectedTab}`]
      );
    });
  }

  if (filteredData && projectFilters.hasOwnProperty("confidence")) {
    filteredData[0] = filteredData[0].filter((item, index) => {
      return !projectFilters["confidence"].includes(
        item["metadata"][`score_confidence_${selectedTab}`]
      );
    });
  }

  return (
    <Layout
      heading="Schedule"
      // setProjectFilters={setProjectFilters}
      // projectFilters={projectFilters}
      // selectedTab={selectedTab}
      // projectData={evaluationData}
    >
      <div className="flex-1 flex flex-col">
        {evaluationData ? (
          <>
            <ButtonSection tabs={tabs} Tab={Tab} setTab={setTab} />
            <ChartSection
              projectData={filteredData}
              selectedTab={selectedTab}
              run_via="schedule"
            />
            <TableSection
              projectData={filteredData}
              selectedTab={selectedTab}
            />
          </>
        ) : (
          <div className="flex justify-center items-center h-screen">
            <SpinningLoader />
          </div>
        )}
      </div>
    </Layout>
  );
};

export default page;
