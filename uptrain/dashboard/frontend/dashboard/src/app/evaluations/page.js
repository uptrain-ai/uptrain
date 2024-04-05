"use client";
import AddProjectModal from "@/components/Evaluations/Homepage/AddProjectModal/AddProjectModal";
import ProjectSection from "@/components/Evaluations/Homepage/ProjectSection";
import Layout from "@/components/Layout";
import SpinningLoader from "@/components/UI/SpinningLoader";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import React, { useLayoutEffect, useState } from "react";
import { useSelector } from "react-redux";

const fetchData = async (uptrainAccessKey, setProjectsData, timeFilter) => {
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
      const responseData = await response.json();
      setProjectsData(
        responseData.filter((item) => item.project_type === "project")
      );
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
  setProjectsData,
  timeFilter,
  projectId
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
      setProjectsData(responseData);
    } else {
      console.error("Failed to submit API Key:", response.statusText);
      // Handle error cases
    }
  } catch (error) {
    console.error("Error submitting API Key:", error.message);
    // Handle network errors or other exceptions
  }
};

const page = () => {
  const [TimeFilter, setTimeFilter] = useState(1);
  const [openModal, setopenModal] = useState(false);
  const [projectsData, setProjectsData] = useState(null);
  const [projectData, setProjectData] = useState(null);
  const [selectedProject, setSelectedProject] = useState(0);

  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  useLayoutEffect(() => {
    const fetchDataAsync = async () => {
      await fetchData(uptrainAccessKey, setProjectsData, TimeFilter);
    };

    if (uptrainAccessKey) fetchDataAsync();
  }, [uptrainAccessKey, TimeFilter]);

  useLayoutEffect(() => {
    const fetchDataAsync = async () => {
      await fetchProjectData(
        uptrainAccessKey,
        setProjectData,
        TimeFilter,
        projectsData[selectedProject].project_id
      );
    };

    if (uptrainAccessKey && projectsData && projectsData.length > 0) {
      fetchDataAsync();
    }
  }, [uptrainAccessKey, TimeFilter, projectsData, selectedProject]);

  const handleProjectChange = (index) => {
    setSelectedProject(index);
  };

  if (projectsData && projectsData.length == 0) {
    return (
      <Layout heading="Evaluations">
        <div className="flex items-center justify-center flex-1 h-full">
          <p className="text-white">Create a new project</p>
        </div>
      </Layout>
    );
  }

  const reloadData = () => {
    setProjectData(null);
    const fetchDataAsync = async () => {
      await fetchProjectData(
        uptrainAccessKey,
        setProjectData,
        TimeFilter,
        projectsData[selectedProject].project_id
      );
    };

    if (uptrainAccessKey && projectsData && projectsData.length > 0)
      fetchDataAsync();
  };

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
    >
      {openModal && (
        <AddProjectModal
          close={() => {
            setopenModal(false);
          }}
          checks={
            projectsData &&
            projectsData.length > 0 &&
            projectsData[selectedProject].checks
          }
          projectId={
            projectsData &&
            projectsData.length > 0 &&
            projectsData[selectedProject].project_id
          }
          reloadData={reloadData}
          projectData={projectData && projectData}
        />
      )}
      <div className="flex-1">
        {projectsData ? (
          <ProjectSection
            data={projectData}
            setopenModal={() => {
              setopenModal(true);
            }}
            project={
              projectsData &&
              projectsData.length > 0 &&
              projectsData[selectedProject].project_name
            }
          />
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
