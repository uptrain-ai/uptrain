"use client";

import PivotTable from "@/components/PivotTable/PivotTable";
import FilterSection from "@/components/FilterSection/FilterSection";
import Layout from "@/components/Layout";
import React, { useEffect, useLayoutEffect, useState } from "react";
import ChartSection from "@/components/Experiment/ChartSection";
import TableSection from "@/components/Experiment/Logs_InsightsTable";
import { useSelector } from "react-redux";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import SpinningLoader from "@/components/UI/SpinningLoader";
import ButtonSection from "@/components/Common/ButtonSection";

const fetchData = async (uptrainAccessKey, setData, timeFilter) => {
  const num_days =
    timeFilter === 0 ? 1 : timeFilter === 1 ? 7 : timeFilter === 2 ? 30 : 10000;

  try {
    const response = await fetch(
      process.env.NEXT_PUBLIC_BACKEND_URL +
        `api/public/get_experiments_list?num_days=${num_days}`,
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
      setData(responseData.data);
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
  setData,
  projectName,
  TimeFilter
) => {
  const num_days =
    TimeFilter === 0 ? 1 : TimeFilter === 1 ? 7 : TimeFilter === 2 ? 30 : 10000;

  try {
    const response = await fetch(
      process.env.NEXT_PUBLIC_BACKEND_URL +
        `api/public/get_project_data?project_name=${projectName}&num_days=${num_days}`,
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
      setData(responseData.data);
    } else {
      console.error("Failed to submit API Key:", response.statusText);
      setData(null);
      // Handle error cases
    }
  } catch (error) {
    console.error("Error submitting API Key:", error.message);
    setData(null);

    // Handle network errors or other exceptions
  }
};

const page = () => {
  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  const [TimeFilter, setTimeFilter] = useState(1);
  const [data, setData] = useState([]);
  const [projectData, setProjectData] = useState(null);
  const [selectedProject, setSelectedProject] = useState(0);
  const [Tab, setTab] = useState(0);

  const tabs = projectData && projectData[4];

  const handleProjectChange = (index) => {
    setSelectedProject(index);
  };

  const projectNames = data.length !== 0 ? data.map((obj) => obj.project) : [];

  useLayoutEffect(() => {
    const fetchDataAsync = async () => {
      await fetchData(uptrainAccessKey, setData, TimeFilter);
    };

    if (uptrainAccessKey) fetchDataAsync();
  }, [uptrainAccessKey, TimeFilter]); // Dependency array to re-run effect when uptrainAccessKey changes

  useEffect(() => {
    setProjectData(null);
    const fetchProjectDataAsync = async () => {
      await fetchProjectData(
        uptrainAccessKey,
        setProjectData,
        projectNames[selectedProject],
        TimeFilter
      );
    };

    if (uptrainAccessKey && data.length !== 0) {
      fetchProjectDataAsync();
    }
  }, [uptrainAccessKey, data, selectedProject, TimeFilter]);

  return (
    <Layout
      heading="Experiment"
      project={projectNames[selectedProject]}
      TimeFilter={TimeFilter}
      setTimeFilter={setTimeFilter}
      duration
      models
      projectNames={projectNames}
      selectedProject={selectedProject}
      handleProjectChange={handleProjectChange}
    >
      <div className="flex gap-10 w-full items-start">
        <div className="flex-1">
          {projectData ? (
            <>
              <ButtonSection tabs={tabs} Tab={Tab} setTab={setTab} />
              <ChartSection
                TimeFilter={TimeFilter}
                projectData={projectData}
                selectedTab={tabs && tabs[Tab]}
              />
              <TableSection
                projectData={projectData}
                selectedTab={tabs && tabs[Tab]}
              />
            </>
          ) : !projectNames[selectedProject] ? (
            <div className="flex justify-center items-center h-screen">
              <p className="font-medium text-lg text-white">
                No Projects found for this duration
              </p>
            </div>
          ) : (
            <div className="flex justify-center items-center h-screen">
              <SpinningLoader />
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default page;
