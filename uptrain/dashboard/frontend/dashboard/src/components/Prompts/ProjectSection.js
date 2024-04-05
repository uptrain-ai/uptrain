import React from "react";
import AddNewProjectCard from "./AddNewProjectCard";
import ProjectCard from "./ProjectCard";
import Link from "next/link";

const ProjectSection = (props) => {
  return (
    <div className="flex-1 mb-5 flex flex-col gap-5">
      <h2 className="font-medium text-[#5C5C66]">
        {props.promptName ? <Link href="/prompts" className="underline">All Prompts</Link> : "All Prompts"}
        {props.promptName ? ` / ${props.promptName}` : ""}
      </h2>
      {props.projectData &&
        props.projectData.map((item, index) => (
          <ProjectCard
            data={item}
            promptName={item.prompt_name}
            openModal={props.openModal}
            setPromptName={props.setPromptName}
            key={index}
            promptProjectName={props.promptProjectName}
            viewEvals={props.viewEvals}
            evaluationId={item.evaluation_id}
          />
        ))}
      <AddNewProjectCard onClick={props.openModal} />
    </div>
  );
};

export default ProjectSection;
