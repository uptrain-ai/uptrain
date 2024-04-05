import React, { useState } from "react";
import UploadDatasetButton from "./UploadDatasetButton";
import CustomSelect from "@/components/CustomSelect/CustomSelect";
import ModelSelector from "@/components/Common/ModelSelector";
import Step2OverModal from "@/components/Common/Step2OverModal";

const Step1 = (props) => {
  const [error, setError] = useState(false);
  const [openModal, setOpenModal] = useState(false);

  const handleSubmit = (event) => {
    event.preventDefault();

    if (
      props.projectData.some(
        (obj) => obj.evaluation_name === props.evaluationName
      )
    ) {
      setError("Cannot create an experiment with previously used name");
      return;
    }

    props.next();
  };

  const handleDatasetSelect = (value) => {
    props.setSelectedDataset(props.dataSetOptions.indexOf(value));
  };

  return (
    <>
      {openModal && (
        <Step2OverModal
          selectedKey={props.selectedOption}
          close={() => setOpenModal(false)}
          data={props.models}
          metadata={props.metadata}
          setMetadata={props.setMetadata}
        />
      )}
      <h2 className="text-lg text-[#B0B0B1] font-medium mb-5">
        New Experiment
      </h2>
      <form onSubmit={handleSubmit}>
        <input
          className="bg-[#171721] rounded-xl px-6 py-4 text-[#B6B6B9] w-full"
          placeholder="Experiment Name"
          required
          value={props.evaluationName}
          onChange={(e) => props.setEvaluationName(e.target.value)}
        />
        <ModelSelector
          selectedOption={props.selectedOption}
          models={props.models}
          metadata={props.metadata}
          setMetadata={props.setMetadata}
          setSelectedOption={props.setSelectedOption}
          setOpenModal={setOpenModal}
        />
        {props.selectedFile ? (
          <>
            <input
              className="bg-[#171721] rounded-xl px-6 py-4 text-[#B6B6B9] w-full mt-5"
              placeholder="Dataset Name"
              required
              value={props.datasetName}
              onChange={(e) => props.setDatasetName(e.target.value)}
            />
            <div className="bg-[#171721] rounded-xl px-6 py-4 text-white w-full my-5 flex justify-between items-center">
              <p>{props.selectedFile.name}</p>
              <button onClick={() => props.setSelectedFile(null)}>x</button>
            </div>
          </>
        ) : (
          <CustomSelect
            selectedOption={props.dataSetOptions[props.dataset]}
            setSelectedOption={handleDatasetSelect}
            options={props.dataSetOptions}
            placeholder="Upload dataset"
            className="rounded-xl px-6 py-4 mb-5"
            required
          />
        )}
        {(props.dataset === null || props.dataset === -1) && (
          <UploadDatasetButton setSelectedFile={props.setSelectedFile} />
        )}
        <input
          className="bg-[#171721] rounded-xl px-6 py-4 text-[#B6B6B9] w-full disabled:bg-[#1f1f29] disabled:text-[#959393] mt-5"
          placeholder="Experiment column"
          onChange={(e) => {
            props.setMetadata({
              ...props.metadata, // Removed square brackets from props.metadata
              exp_column: e.target.value,
            });
          }}
          value={
            props.metadata["exp_column"] ? props.metadata["exp_column"] : ""
          }
          required
        />
        <p className="text-red-500">{error}</p>
        <div className="flex justify-end mt-5">
          <button
            type="Submit"
            className="bg-[#5587FD] text-white px-10 py-2.5 font-semibold text-lg rounded-xl"
          >
            Next
          </button>
        </div>
      </form>
    </>
  );
};

export default Step1;
