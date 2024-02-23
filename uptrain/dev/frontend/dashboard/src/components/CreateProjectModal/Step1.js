import React, { useRef } from "react";
import CustomSelect from "../CustomSelect/CustomSelect";

const Step1 = (props) => {
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    props.setSelectedFile(event.target.files[0]);
  };

  const handleButtonClick = () => {
    fileInputRef.current.click();
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    props.promptProjectName
      ? props.nextPrompt()
      : props.selectedProjectType === "Evaluation"
      ? props.nextEvaluation()
      : props.nextPrompt();
  };

  return (
    <div>
      <h2 className="text-lg text-[#B0B0B1] font-medium mb-5">New project</h2>
      <form onSubmit={handleSubmit}>
        <input
          className="bg-[#171721] rounded-xl px-6 py-4 text-[#B6B6B9] w-full"
          placeholder="Project name"
          onChange={(e) => props.setProjectName(e.target.value)}
          value={
            props.promptProjectName
              ? props.promptProjectName
              : props.projectName
          }
          required
          disabled={props.promptProjectName}
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
          accept=".jsonl,.json"
          onChange={handleFileChange}
          ref={fileInputRef}
          style={{ display: "none" }}
          required
        />
        {!props.promptProjectName && (
          <CustomSelect
            selectedOption={props.selectedProjectType}
            setSelectedOption={props.setSelectedProjectType}
            options={["Evaluation", "Prompt"]}
            placeholder="Select Project Type"
            className="rounded-xl px-6 py-4"
            required
          />
        )}
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
        <CustomSelect
          selectedOption={props.selectedOption}
          setSelectedOption={props.setSelectedOption}
          options={props.models}
          placeholder="Select Evaluation LLM"
          className="rounded-xl px-6 py-4"
          required
        />
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
