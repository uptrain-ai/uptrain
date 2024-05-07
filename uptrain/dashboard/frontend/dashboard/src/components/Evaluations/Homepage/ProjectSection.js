import React from "react";
import ProjectCard from "./ProjectCard";
import CreateProjectTab from "../../Common/CreateProjectTab";

const ProjectSection = (props) => {
  return (
    <>
      <h2 className="font-medium text-[#5C5C66] mb-5">Your Projects</h2>
      <div className="grid grid-cols-2 gap-5">
        {props.data &&
          props.data
            .filter((item) => item.run_type == "evaluation")
            .map((item, index) => (
              <ProjectCard
                key={index}
                title={item.evaluation_name}
                date={item.created_at}
                project={props.project}
                evaluation={item.evaluation_name}
                evaluation_id={item.evaluation_id}
              />
            ))}
        <CreateProjectTab
          onClick={props.setopenModal}
          title="Create New Evaluation"
        />
      </div>
    </>
  );
};

export default ProjectSection;
