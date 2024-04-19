import React, { useState } from "react";
import Row from "./Row";
import Divider from "../Evaluations/ChartPage/Logs/Divider";
import { useRouter } from "next/navigation";
import EvaluationModal from "./EvaluationModal/EvaluationModal";

const ProjectCard = (props) => {
  const [expand, setExpand] = useState(false);
  const [openModal, setOpenModal] = useState(null);
  const router = useRouter();

  const handleCreateNewVersion = (e) => {
    e.stopPropagation();
    props.setPromptName(props.data.prompt_name);
    props.openModal();
  };

  const handleViewAllVersion = (e) => {
    e.stopPropagation();
    router.push(
      `/prompts/${props.promptProjectName}/${props.data.prompt_name}`
    );
  };

  return (
    <div
      className={`bg-[#23232D] rounded-xl p-8 text-red-400 border border-[#23232D] hover:bg-[#171721] hover:border-[#5587fd] ${
        !props.viewEvals && "cursor-pointer"
      }`}
      onMouseEnter={() => setExpand(true)}
      onMouseLeave={() => setExpand(false)}
      onClick={!props.viewEvals ? handleViewAllVersion : () => {}}
    >
      {openModal && (
        <EvaluationModal
          onClick={() => setOpenModal(null)}
          evaluationId={props.evaluationId}
          data={props.data}
          heading="Evaluations"
        />
      )}
      <Row
        data={props.data}
        promptName={props.prompt_name}
        expand={expand}
        setExpand={setExpand}
      />
      {expand && (
        <>
          <div className="flex justify-end mt-5 gap-3">
            {props.viewEvals ? (
              <>
                <button
                  className="text-base font-semibold text-white border-2 border-[#3D75F7] bg-[#3D75F7] rounded-xl py-3 px-5 hover:bg-[#171721]"
                  onClick={() => setOpenModal(true)}
                >
                  View Evals Details
                </button>
              </>
            ) : (
              <>
                <button
                  className="text-base font-semibold text-white border-2 border-[#3D75F7] rounded-xl py-3 px-5 hover:bg-[#171721]"
                  onClick={handleViewAllVersion}
                >
                  View All Version
                </button>
                <button
                  className="text-base font-semibold text-white border-2 border-[#3D75F7] bg-[#3D75F7] rounded-xl py-3 px-5 hover:bg-[#171721]"
                  onClick={handleCreateNewVersion}
                >
                  Create New Version
                </button>
              </>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default ProjectCard;
