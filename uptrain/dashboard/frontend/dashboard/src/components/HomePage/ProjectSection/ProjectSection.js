import React from "react";
import ProjectCard from "./ProjectCard";
import CreateProjectTab from "./CreateProjectTab";

const ProjectSection = (props) => {
  return (
    <>
      <h2 className="font-medium text-[#5C5C66] mb-5">Your Projects</h2>
      <div className="grid grid-cols-2 gap-5">
        {props.data &&
          props.data.map((item, index) => (
            <ProjectCard
              key={index}
              title={item.project}
              health={item.health}
              date={item.latest_timestamp}
              run_via={item.run_via}
            />
          ))}
        <CreateProjectTab setopenModal={props.setopenModal} />
      </div>
    </>
  );
};

export default ProjectSection;
