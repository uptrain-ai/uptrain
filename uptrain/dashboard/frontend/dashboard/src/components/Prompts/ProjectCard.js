import React, { useState } from "react";
import Row from "./Row";
import Divider from "../Evaluations/Logs/Divider";

const ProjectCard = (props) => {
  const [expand, setExpand] = useState(false);

  const handleCreateNewVersion = () => {
    props.setPromptVersionName(props.data.prompt_name);
    props.openModal();
  };

  return (
    <div className="bg-[#23232D] rounded-xl p-8 text-red-400 ">
      {props.selectedVersion1 != null || props.selectedVersion2 != null ? (
        <>
          {props.selectedVersion1 != null && (
            <Row data={props.data.prompts[props.selectedVersion1]} />
          )}
          {props.selectedVersion1 != null && props.selectedVersion2 != null && (
            <Divider />
          )}
          {props.selectedVersion2 != null && (
            <Row data={props.data.prompts[props.selectedVersion2]} />
          )}
        </>
      ) : (
        <Row
          data={props.data.prompts[0]}
          promptName={props.data.prompt_name}
          expand={expand}
          setExpand={setExpand}
        />
      )}
      {props.selectedVersion1 == null &&
        props.selectedVersion2 == null &&
        expand &&
        props.data.prompts.slice(1).map((item, index) => (
          <div key={index}>
            <Divider />
            <Row data={item} />
          </div>
        ))}
      {props.selectedVersion1 == null &&
        props.selectedVersion2 == null &&
        expand && (
          <>
            <div className="flex justify-end mt-5">
              <button
                className="text-base font-semibold text-white border-2 border-[#3D75F7] rounded-xl py-3 px-5 hover:bg-[#171721]"
                onClick={handleCreateNewVersion}
              >
                Create New Version
              </button>
            </div>
          </>
        )}
    </div>
  );
};

export default ProjectCard;
