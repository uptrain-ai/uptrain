import React, { useRef, useState } from "react";
import ModelSelector from "../Common/ModelSelector";
import Step2OverModal from "../Common/Step2OverModal";

const Step1 = (props) => {
  const [error, setError] = useState();
  const [isExperiment, setIsExperiment] = useState(false);
  const [openModal, setOpenModal] = useState(false);

  const projectName = props.projectName;
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    props.setSelectedFile(event.target.files[0]);
  };

  const handleButtonClick = () => {
    fileInputRef.current.click();
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    if (props.projectNames.includes(projectName)) {
      setError("Cannot create an evaluation with previously used name");
      return;
    }

    if (!props.selectedFile) {
      setError("Please upload a dataset");
      return;
    }

    props.next();
  };

  return (
    <div>
      {openModal && (
        <Step2OverModal
          selectedKey={props.selectedOption}
          close={() => setOpenModal(false)}
          data={props.models}
          metadata={props.metadata}
          setMetadata={props.setMetadata}
        />
      )}
      <h2 className="text-lg text-[#B0B0B1] font-medium mb-5">New project</h2>
      <form onSubmit={handleSubmit}>
        <input
          className="bg-[#171721] rounded-xl px-6 py-4 text-[#B6B6B9] w-full"
          placeholder="Project name"
          onChange={(e) => props.setProjectName(e.target.value)}
          value={projectName}
          required
        />
        <input
          className="bg-[#171721] rounded-xl px-6 py-4 text-[#B6B6B9] w-full mt-5"
          placeholder="Dataset name"
          onChange={(e) => props.setDatasetName(e.target.value)}
          value={props.datasettName}
          required
        />
        <input
          type="file"
          accept=".jsonl"
          onChange={handleFileChange}
          ref={fileInputRef}
          style={{ display: "none" }}
        />
        <button
          type="button"
          onClick={handleButtonClick}
          className="bg-[#171721] rounded-xl px-6 py-4 text-[#B6B6B9] w-full flex items-start justify-start mt-5"
        >
          {props.selectedFile ? (
            <span>{props.selectedFile.name}</span>
          ) : (
            "Choose File"
          )}
        </button>
        <p className="text-sm text-white px-6 mt-1">
          Only .jsonl format supported
        </p>
        <ModelSelector
          selectedOption={props.selectedOption}
          models={props.models}
          metadata={props.metadata}
          setMetadata={props.setMetadata}
          setSelectedOption={props.setSelectedOption}
          setOpenModal={setOpenModal}
        />
        <div className="flex gap-2 mt-5 mb-1 items-center">
          <p className="text-[#868686] text-sm">
            Use same info to run Experiments
          </p>
          <div className="flex">
            <button
              type="button"
              className={`${
                !isExperiment
                  ? "text-[#ffffff] bg-[#5587FD]"
                  : "text-[#868686] bg-[#171721]"
              } py-1 px-1.5 rounded-l-lg`}
              onClick={() => {
                props.setMetadata((prevState) => {
                  const { exp_column, ...rest } = prevState;
                  return rest;
                });
                setIsExperiment(false);
              }}
            >
              No
            </button>
            <button
              type="button"
              className={`${
                isExperiment
                  ? "text-[#ffffff] bg-[#5587FD]"
                  : "text-[#868686] bg-[#171721] "
              } py-1 px-1.5 rounded-r-lg`}
              onClick={() => {
                props.setMetadata((prevState) => {
                  return { ...prevState, exp_column: "" };
                });
                setIsExperiment(true);
              }}
            >
              Yes
            </button>
          </div>
        </div>
        <input
          className="bg-[#171721] rounded-xl px-6 py-4 text-[#B6B6B9] w-full mt-1 disabled:bg-[#1f1f29] disabled:opacity-70 disabled:text-[#959393]"
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
          required={isExperiment}
          disabled={!isExperiment}
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
    </div>
  );
};

export default Step1;
