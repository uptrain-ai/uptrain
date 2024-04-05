"use client";
import Layout from "@/components/Layout";
import AddProjectModal from "@/components/Prompts/AddProjectModal/AddProjectModal";
import ProjectSection from "@/components/Prompts/ProjectSection";
import SpinningLoader from "@/components/UI/SpinningLoader";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import { useRouter } from "next/navigation";
import { useEffect, useLayoutEffect, useState } from "react";
import { useSelector } from "react-redux";

const fetchData = async (
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
  projectId
) => {
  try {
    const response = await fetch(
      process.env.NEXT_PUBLIC_BACKEND_URL +
        `api/public/prompt_runs?project_id=${projectId}`,
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
      setProjectData(responseData);
    } else {
      console.error("Failed to submit API Key:", response.statusText);
      setProjectData(null);
    }
  } catch (error) {
    console.error("Error submitting API Key:", error.message);
    setProjectData(null);
  }
};

const PromptsPage = (props) => {
  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  const router = useRouter();

  const [timeFilter, setTimeFilter] = useState(1);
  const [selectedProject, setSelectedProject] = useState(0);
  const [projectsData, setProjectsData] = useState(null);
  const [projectData, setProjectData] = useState([]);
  const [openModal, setOpenModal] = useState(false);

  useLayoutEffect(() => {
    const fetchDataAsync = async () => {
      await fetchData(
        uptrainAccessKey,
        setProjectsData,
        timeFilter,
        props.slug[0],
        setSelectedProject
      );
    };

    if (uptrainAccessKey) fetchDataAsync();
  }, [uptrainAccessKey, timeFilter]); // Dependency array to re-run effect when uptrainAccessKey changes

  useEffect(() => {
    setProjectData(null);
    const fetchProjectDataAsync = async () => {
      await fetchProjectData(
        uptrainAccessKey,
        setProjectData,
        projectsData[selectedProject].project_id,
        timeFilter
      );
    };

    if (uptrainAccessKey && projectsData) {
      fetchProjectDataAsync();
    }
  }, [uptrainAccessKey, projectsData, selectedProject]);

  const handleProjectChange = (index) => {
    router.replace(`/prompts/${projectsData[index].project_name}`);
  };

  const reloadData = () => {
    setProjectData(null);
    const fetchProjectDataAsync = async () => {
      await fetchProjectData(
        uptrainAccessKey,
        setProjectData,
        projectsData[selectedProject].project_id,
        timeFilter
      );
    };

    if (uptrainAccessKey && projectsData) {
      fetchProjectDataAsync();
    }
  };

  const prompts = projectData && projectData.map((item) => item.prompt_name);

  return (
    <Layout
      heading="Prompts"
      project={
        projectsData &&
        projectsData.length > 0 &&
        projectsData[selectedProject].project_name
      }
      TimeFilter={timeFilter}
      setTimeFilter={setTimeFilter}
      duration
      projectNames={
        projectsData &&
        projectsData.length > 0 &&
        projectsData.map((item) => item.project_name)
      }
      selectedProject={selectedProject}
      handleProjectChange={handleProjectChange}
      prompts={[...new Set(prompts)]}
      selectedPrompt={decodeURIComponent(props.slug[1])}
      projectData={
        projectData &&
        projectData.filter(
          (item) => item.prompt_name === decodeURIComponent(props.slug[1])
        )
      }
      compare
    >
      {openModal && (
        <AddProjectModal
          close={() => {
            setOpenModal(false);
          }}
          databaseId={
            projectsData &&
            projectsData.length > 0 &&
            projectsData[selectedProject].dataset_id
          }
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
          promptName={decodeURIComponent(props.slug[1])}
          setPromptName={() => {}}
        />
      )}
      <div className="flex gap-10 w-full items-start">
        {projectData ? (
          <ProjectSection
            projectData={projectData.filter(
              (item) => item.prompt_name === decodeURIComponent(props.slug[1])
            )}
            openModal={() => setOpenModal(true)}
            promptProjectName={
              projectsData &&
              projectsData.length > 0 &&
              projectsData[selectedProject].project_name
            }
            viewEvals
            promptName={decodeURIComponent(props.slug[1])}
          />
        ) : (
          <div className="flex flex-1 justify-center items-center h-screen">
            <SpinningLoader />
          </div>
        )}
      </div>
    </Layout>
  );
};

export default PromptsPage;
