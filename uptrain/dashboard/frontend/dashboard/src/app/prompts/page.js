"use client";
import CompareSection from "@/components/CompareSection/CompareSection";
import CreateProjectModal from "@/components/CreateProjectModal/CreateProjectModal";
import FilterSection from "@/components/FilterSection/FilterSection";
import Layout from "@/components/Layout";
import ProjectSection from "@/components/Prompts/ProjectSection";
import SpinningLoader from "@/components/UI/SpinningLoader";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import { useEffect, useLayoutEffect, useState } from "react";
import { useSelector } from "react-redux";

const fetchData = async (uptrainAccessKey, setData, timeFilter) => {
  const num_days =
    timeFilter === 0 ? 1 : timeFilter === 1 ? 7 : timeFilter === 2 ? 30 : 10000;

  try {
    const response = await fetch(
      process.env.NEXT_PUBLIC_BACKEND_URL +
        `api/public/get_prompts_list?num_days=${num_days}`,
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
        `api/public/get_prompt_data?project_name=${projectName}&num_days=${num_days}`,
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

const page = () => {
  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  const [timeFilter, setTimeFilter] = useState(1);
  const [selectedProject, setSelectedProject] = useState(0);
  const [data, setData] = useState(null);
  const [projectData, setProjectData] = useState(null);
  const [openModal, setOpenModal] = useState(false);
  const [promptVersionName, setPromptVersionName] = useState(null);
  const [selectedCompareProject, setSelectedCompareProject] = useState(null);
  const [selectedVersion1, setSelectedVersion1] = useState(null);
  const [selectedVersion2, setSelectedVersion2] = useState(null);

  const projectNames = data ? data.map((obj) => obj.project) : [];
  

  const filteredProjects =
    projectData && projectData.filter((item) => item.prompts.length > 1);

  useLayoutEffect(() => {
    const fetchDataAsync = async () => {
      await fetchData(uptrainAccessKey, setData, timeFilter);
    };

    if (uptrainAccessKey) fetchDataAsync();
  }, [uptrainAccessKey, timeFilter]); // Dependency array to re-run effect when uptrainAccessKey changes

  useEffect(() => {
    setSelectedCompareProject(null);
    setProjectData(null);
    const fetchProjectDataAsync = async () => {
      await fetchProjectData(
        uptrainAccessKey,
        setProjectData,
        projectNames[selectedProject],
        timeFilter
      );
    };

    if (uptrainAccessKey && data) {
      fetchProjectDataAsync();
    }
  }, [uptrainAccessKey, data, selectedProject]);

  useEffect(() => {
    setSelectedVersion1(null);
    setSelectedVersion2(null);
  }, [selectedCompareProject]);

  const handleProjectChange = (index) => {
    setSelectedProject(index);
  };

  const reloadData = () => {
    const fetchProjectDataAsync = async () => {
      await fetchProjectData(
        uptrainAccessKey,
        setProjectData,
        projectNames[selectedProject],
        timeFilter
      );
    };

    setProjectData(null);
    fetchProjectDataAsync();
  };

  return (
    <Layout
      heading="Prompts"
      project={projectNames[selectedProject]}
      TimeFilter={timeFilter}
      setTimeFilter={setTimeFilter}
      duration
      projectNames={projectNames}
      selectedProject={selectedProject}
      handleProjectChange={handleProjectChange}
      projectData={projectData}
      compare
      filteredProjects={filteredProjects}
      selectedCompareProject={selectedCompareProject}
      setSelectedCompareProject={setSelectedCompareProject}
      selectedVersion1={selectedVersion1}
      setSelectedVersion1={setSelectedVersion1}
      selectedVersion2={selectedVersion2}
      setSelectedVersion2={setSelectedVersion2}
    >
      {openModal && (
        <CreateProjectModal
          close={() => {
            setOpenModal(false);
          }}
          reloadData={reloadData}
          promptProjectName={projectNames[selectedProject]}
          promptVersionName={promptVersionName}
        />
      )}
      <div className="flex gap-10 w-full items-start">
        {projectData ? (
          <ProjectSection
            projectData={projectData}
            openModal={() => setOpenModal(true)}
            setPromptVersionName={setPromptVersionName}
            selectedCompareProject={selectedCompareProject}
            filteredProjects={filteredProjects}
            selectedVersion1={selectedVersion1}
            selectedVersion2={selectedVersion2}
          />
        ) : !projectNames[selectedProject] ? (
          <div className="flex flex-1 justify-center items-center h-screen">
            <p className="font-medium text-lg text-white">
              No Projects found for this duration
            </p>
          </div>
        ) : (
          <div className="flex flex-1 justify-center items-center h-screen">
            <SpinningLoader />
          </div>
        )}
      </div>
    </Layout>
  );
};

export default page;
