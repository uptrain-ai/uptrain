import React from "react";
import ProjectCard from "./ProjectCard";
import CreateProjectTab from "@/components/Common/CreateProjectTab";
import { changeDateFormat } from "@/utils/changeDateFormat";

const ProjectSection = (props) => {
  return (
    <>
      <h2 className="font-medium text-[#5C5C66] mb-5">Your Projects</h2>
      <div className="grid grid-cols-2 gap-5">
        {props.data &&
            props.data.map((item, index) => (
            <ProjectCard
              key={index}
              title={item.project_name}
              date={item.created_at}
              projectType={item.project_type}
              projectId={item.project_id}
            />
          ))}
        <CreateProjectTab onClick={props.setopenModal} />
      </div>
    </>
  );
};

export default ProjectSection;
