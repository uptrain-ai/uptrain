"use client";
import ButtonSection from "@/components/Common/ButtonSection";
import ChartSection from "@/components/Evaluations/ChartPage/ChartSection";
import TableSection from "@/components/Evaluations/ChartPage/Logs_InsightsTable";
import Layout from "@/components/Layout";
import SpinningLoader from "@/components/UI/SpinningLoader";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import { useRouter } from "next/navigation";
import React, { useLayoutEffect, useState } from "react";
import { useSelector } from "react-redux";

const fetchProjectsData = async (
  uptrainAccessKey,
  setProjectsData,
  timeFilter,
  slug,
  setSelectedProject,
  router
) => {
  const num_days =
    timeFilter === 0 ? 1 : timeFilter === 1 ? 7 : timeFilter === 2 ? 30 : 10000;

  try {
    const response = await fetch(
      process.env.NEXT_PUBLIC_BACKEND_URL +
        `api/public/projects?num_days=${num_days}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "uptrain-access-token": `${uptrainAccessKey}`,
        },
      }
    );

    if (response.ok) {
      let responseData = await response.json();
      responseData = responseData.filter(
        (item) => item.project_type === "project"
      );
      setProjectsData(responseData);

      slug = decodeURIComponent(slug);

      const projectIndex = responseData.findIndex(
        (project) => project.project_name === slug
      );

      if (projectIndex != -1) {
        setSelectedProject(projectIndex);
      } else {
        router.replace("/404");
      }
    } else {
      console.error("Failed to submit API Key:", response.statusText);
      // Handle error cases
    }
  } catch (error) {
    console.error("Error submitting API Key:", error.message);
    // Handle network errors or other exceptions
  }
};

const fetchProjectData = async (
  uptrainAccessKey,
  setProjectData,
  timeFilter,
  projectId,
  slug,
  setEvaluationId,
  router
) => {
  const num_days =
    timeFilter === 0 ? 1 : timeFilter === 1 ? 7 : timeFilter === 2 ? 30 : 10000;

  try {
    const response = await fetch(
      process.env.NEXT_PUBLIC_BACKEND_URL +
        `api/public/project_runs?num_days=${num_days}&project_id=${projectId}`,
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

      slug = decodeURIComponent(slug);

      const projectIndex = responseData.findIndex(
        (project) => project.evaluation_name === slug
      );

      if (projectIndex != -1) {
        setEvaluationId(responseData[projectIndex].evaluation_id);
      } else {
        router.replace("/404");
      }

      setProjectData(responseData);
    } else {
      console.error("Failed to submit API Key:", response.statusText);
      // Handle error cases
    }
  } catch (error) {
    console.error("Error submitting API Key:", error.message);
    // Handle network errors or other exceptions
  }
};

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

const ChartPage = (props) => {
  const router = useRouter();

  const [TimeFilter, setTimeFilter] = useState(1);
  const [projectsData, setProjectsData] = useState(null);
  const [projectData, setProjectData] = useState(null);
  const [selectedProject, setSelectedProject] = useState(0);
  const [evaluationId, setEvaluationId] = useState(null);
  const [evaluationData, setEvaluationData] = useState(null);
  const [Tab, setTab] = useState(0);
  const [projectFilters, setProjectFilters] = useState({});

  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  const tabs = evaluationData && evaluationData[2];
  const selectedTab = tabs && tabs[Tab];

  useLayoutEffect(() => {
    const fetchDataAsync = async () => {
      await fetchProjectsData(
        uptrainAccessKey,
        setProjectsData,
        TimeFilter,
        props.slug[0],
        setSelectedProject
      );
    };

    if (uptrainAccessKey) fetchDataAsync();
  }, [uptrainAccessKey, TimeFilter]);

  useLayoutEffect(() => {
    const fetchDataAsync = async () => {
      await fetchProjectData(
        uptrainAccessKey,
        setProjectData,
        TimeFilter,
        projectsData[selectedProject].project_id,
        props.slug[1],
        setEvaluationId,
        router
      );
    };

    if (uptrainAccessKey && projectsData && projectsData.length > 0) {
      fetchDataAsync();
    }
  }, [uptrainAccessKey, TimeFilter, projectsData, selectedProject]);

  useLayoutEffect(() => {
    const fetchDataAsync = async () => {
      await fetchEvaluationData(
        uptrainAccessKey,
        evaluationId,
        setEvaluationData
      );
    };

    if (uptrainAccessKey && evaluationId) {
      fetchDataAsync();
    }
  }, [uptrainAccessKey, evaluationId]);

  const handleProjectChange = (index) => {
    router.replace(`/evaluations/${projectsData[index].project_name}`);
  };

  var filteredData = JSON.parse(JSON.stringify(evaluationData));

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
      return !projectFilters["scores"].includes(item[`score_${selectedTab}`]);
    });
  }

  if (filteredData && projectFilters.hasOwnProperty("confidence")) {
    filteredData[0] = filteredData[0].filter((item, index) => {
      return !projectFilters["confidence"].includes(
        item[`score_confidence_${selectedTab}`]
      );
    });
  }

  if (filteredData) {
    Object.entries(projectFilters).map(([key, value]) => {
      if (key != "index" && key != "scores" && key != "confidence") {
        if (
          projectFilters[key].filterCondition == "contains" &&
          projectFilters[key].filterinput
        ) {
          filteredData[0] = filteredData[0].filter((item) => {
            return item[key].includes(projectFilters[key].filterinput);
          });
        }

        if (
          projectFilters[key].filterCondition == "does not contain" &&
          projectFilters[key].filterinput
        ) {
          filteredData[0] = filteredData[0].filter((item) => {
            return item[key].indexOf(projectFilters[key].filterinput) == -1;
          });
        }

        if (
          projectFilters[key].filterCondition == "starts with" &&
          projectFilters[key].filterinput
        ) {
          filteredData[0] = filteredData[0].filter((item) => {
            return item[key].startsWith(projectFilters[key].filterinput);
          });
        }

        if (
          projectFilters[key].filterCondition == "ends with" &&
          projectFilters[key].filterinput
        ) {
          filteredData[0] = filteredData[0].filter((item) => {
            return item[key].endsWith(projectFilters[key].filterinput);
          });
        }
      }
    });
  }

  return (
    <Layout
      heading="Evaluations"
      project={
        projectsData &&
        projectsData.length > 0 &&
        projectsData[selectedProject].project_name
      }
      TimeFilter={TimeFilter}
      setTimeFilter={setTimeFilter}
      duration
      projectNames={
        projectsData && projectsData.map((item) => item.project_name)
      }
      selectedProject={selectedProject}
      handleProjectChange={handleProjectChange}
      evaluations={
        projectData &&
        projectData.filter((item) => item.run_type === "evaluation")
      }
      evaluationId={evaluationId}
      setProjectFilters={setProjectFilters}
      projectFilters={projectFilters}
      projectData={evaluationData}
      selectedTab={tabs && tabs[Tab]}
    >
      <div className="flex-1 flex flex-col">
        {evaluationData ? (
          <>
            <ButtonSection
              tabs={tabs}
              Tab={Tab}
              setTab={setTab}
              checks={evaluationData[3].checks}
            />
            <ChartSection
              TimeFilter={TimeFilter}
              projectData={filteredData}
              selectedTab={selectedTab}
            />
            <TableSection
              projectData={filteredData}
              selectedTab={selectedTab}
              evaluationId={evaluationId}
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

export default ChartPage;
