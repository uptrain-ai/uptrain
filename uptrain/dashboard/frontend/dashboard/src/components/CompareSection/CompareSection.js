import React, { useState } from "react";
import SingleSelect from "../DropDowns/SingleSelect";
import CompareModal from "../Prompts/CompareModal/CompareModal";

const CompareSection = (props) => {
  const [firstIndex, setFirstIndex] = useState(null);
  const [secondIndex, setSecondIndex] = useState(null);
  const [openModal, setOpenModal] = useState(null);
  const [error, setError] = useState("");

  const handleFirstSelect = (index) => {
    setSecondIndex(null);
    setFirstIndex(index);
  };

  const handleSecondSelect = (index) => {
    setSecondIndex(index);
  };

  const handleSubmit = () => {
    if (firstIndex == secondIndex) {
      setError("Please select different prompts");
      return;
    }

    if (
      props.projectData[firstIndex].dataset_id !=
      props.projectData[secondIndex].dataset_id
    ) {
      setError("Can't compare versions created from different datasets");
      return;
    }

    setOpenModal(true);
  };

  return (
    <div className="mt-10">
      {openModal && (
        <CompareModal
          onClick={() => setOpenModal(null)}
          evaluationId1={props.projectData[firstIndex].evaluation_id}
          evaluationId2={props.projectData[secondIndex].evaluation_id}
          version1={props.projectData[firstIndex].prompt_version}
          version2={props.projectData[secondIndex].prompt_version}
          data1={props.projectData[firstIndex]}
          data2={props.projectData[secondIndex]}
          heading="Compare"
        />
      )}
      <h2 className="text-lg font-medium">Compare Prompts</h2>
      <div className="mt-4">
        <SingleSelect
          title="Select prompt Version"
          placeholder="Select a Version"
          selections={
            props.projectData &&
            props.projectData.map((item) => item.prompt_version)
          }
          selected={firstIndex}
          OnClick={handleFirstSelect}
          prelable="V "
        />
        {firstIndex != null && (
          <SingleSelect
            title="Select prompt Version"
            placeholder="Select a Version"
            selections={
              props.projectData &&
              props.projectData.map((item) => item.prompt_version)
            }
            selected={secondIndex}
            OnClick={handleSecondSelect}
            prelable="V "
          />
        )}
        <p className="text-red-500">{error}</p>
        {secondIndex != null ? (
          <div className="flex justify-end mt-5">
            <button
              className="border-2 border-[#3D75F7] rounded-full py-1.5 px-3 bg-[#171721] font-semibold text-white hover:bg-transparent"
              onClick={handleSubmit}
            >
              Compare
            </button>
          </div>
        ) : (
          <></>
        )}
      </div>
    </div>
  );
};

export default CompareSection;
