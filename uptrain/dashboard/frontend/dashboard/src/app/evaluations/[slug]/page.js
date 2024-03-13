"use client";
import ChartSection from "@/components/Evaluations/ChartSection";
import TableSection from "@/components/Evaluations/Logs_InsightsTable";
import FilterSection from "@/components/FilterSection/FilterSection";
import Layout from "@/components/Layout";
import React, { useEffect, useLayoutEffect, useState } from "react";
import { useSelector } from "react-redux";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import ButtonSection from "@/components/Common/ButtonSection";
import SpinningLoader from "@/components/UI/SpinningLoader";
import { useRouter } from "next/navigation";

const fetchData = async (
  uptrainAccessKey,
  setData,
  timeFilter,
  setSelectedProject,
  slug,
  router
) => {
  const num_days =
    timeFilter === 0 ? 1 : timeFilter === 1 ? 7 : timeFilter === 2 ? 30 : 10000;

  try {
    const response = await fetch(
      process.env.NEXT_PUBLIC_BACKEND_URL +
        `api/public/get_evaluations_list?num_days=${num_days}`,
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

      slug = decodeURIComponent(slug);

      const projectIndex = responseData.data.findIndex(
        (project) => project.project === slug
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
    }
  } catch (error) {
    console.error("Error submitting API Key:", error.message);
    setData(null);
  }
};

const page = ({ params: { slug } }) => {
  const router = useRouter();

  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  const [TimeFilter, setTimeFilter] = useState(3);
  const [data, setData] = useState([]);
  const [projectData, setProjectData] = useState(null);
  const [selectedProject, setSelectedProject] = useState(0);
  const [Tab, setTab] = useState(0);
  const [projectFilters, setProjectFilters] = useState({});

  const tabs = projectData && projectData[4];
  const projectNames = data.length !== 0 ? data.map((obj) => obj.project) : [];

  const handleProjectChange = (index) => {
    setSelectedProject(index);
  };

  useLayoutEffect(() => {
    const fetchDataAsync = async () => {
      await fetchData(
        uptrainAccessKey,
        setData,
        TimeFilter,
        setSelectedProject,
        slug,
        router
      );
    };

    if (uptrainAccessKey) fetchDataAsync();
  }, [uptrainAccessKey, TimeFilter]); // Dependency array to re-run effect when uptrainAccessKey changes

  useEffect(() => {
    setProjectData(null);
    setProjectFilters({});
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

  useEffect(() => {
    setProjectFilters({});
  }, [Tab]);

  const selectedTab = tabs && tabs[Tab];

  let filteredData = JSON.parse(JSON.stringify(projectData));

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
      console.log(item["checks"][`score_${selectedTab}`]);
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
      heading="Evaluations"
      project={projectNames[selectedProject]}
      TimeFilter={TimeFilter}
      setTimeFilter={setTimeFilter}
      duration
      projectNames={projectNames}
      selectedProject={selectedProject}
      handleProjectChange={handleProjectChange}
      setProjectFilters={setProjectFilters}
      projectFilters={projectFilters}
      projectData={projectData}
      selectedTab={selectedTab}
    >
      <div className="flex-1 flex flex-col">
        {projectData ? (
          <>
            <ButtonSection tabs={tabs} Tab={Tab} setTab={setTab} />
            <ChartSection
              TimeFilter={TimeFilter}
              projectData={filteredData}
              run_via={data[selectedProject] && data[selectedProject].run_via}
              selectedTab={selectedTab}
            />
            <TableSection
              projectData={filteredData}
              selectedTab={selectedTab}
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
    </Layout>
  );
};

export default page;
