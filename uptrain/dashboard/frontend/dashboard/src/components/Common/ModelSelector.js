import React from "react";
import CustomSelect from "../CustomSelect/CustomSelect";

const ModelSelector = (props) => {
  const handleModelSelect = (key) => {
    props.setSelectedOption(key);
    if (props.models[key].length > 0) {
      props.setOpenModal(true);
    }
  };

  return (
    <>
      <CustomSelect
        selectedOption={props.selectedOption}
        setSelectedOption={handleModelSelect}
        options={Object.keys(props.models)}
        placeholder="Select Evaluation LLM"
        className="rounded-xl px-6 py-4"
        required
      />
    </>
  );
};

export default ModelSelector;
