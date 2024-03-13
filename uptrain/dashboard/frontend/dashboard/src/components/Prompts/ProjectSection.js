import React from "react";
import AddNewProjectCard from "./AddNewProjectCard";
import ProjectCard from "./ProjectCard";

const ProjectSection = (props) => {
  return (
    <div className="flex-1 mb-5 flex flex-col gap-5">
      <h2 className="font-medium text-[#5C5C66]">All Prompts</h2>
      {props.selectedCompareProject != null
        ? props.filteredProjects && (
            <ProjectCard
              data={props.filteredProjects[props.selectedCompareProject]}
              openModal={props.openModal}
              setPromptVersionName={props.setPromptVersionName}
              expanded
              selectedVersion1={props.selectedVersion1}
              selectedVersion2={props.selectedVersion2}
            />
          )
        : props.projectData &&
          props.projectData.map((item, index) => (
            <ProjectCard
              data={item}
              openModal={props.openModal}
              setPromptVersionName={props.setPromptVersionName}
              key={index}
            />
          ))}
      <AddNewProjectCard onClick={props.openModal} />
    </div>
  );
};

export default ProjectSection;
