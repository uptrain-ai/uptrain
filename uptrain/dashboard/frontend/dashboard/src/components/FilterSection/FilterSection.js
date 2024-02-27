"use client";
import React, { useState } from "react";
import SingleSelect from "../UI/SingleSelect";

const CustomMultiCheckBox = (props) => {
  const [isChecked, setChecked] = useState(false);

  // Function to handle checkbox state change
  const handleCheckboxChange = () => {
    setChecked(!isChecked);
  };

  return (
    <div className="flex gap-3 items-center">
      <input
        type="checkbox"
        checked={isChecked}
        onChange={handleCheckboxChange}
      />
      <label className="text-[#B6B6B9] font-medium">{props.title}</label>
    </div>
  );
};

const MultiSelect = (props) => {
  const [Selected, setSelected] = useState(false);

  return (
    <div className="mt-4">
      {props.title && (
        <h3 className="font-medium text-sm mb-1">{props.title}</h3>
      )}
      <div className="relative h-8">
        <div className="bg-[#171721] rounded-2xl px-2.5 py-1 ">
          <div
            className="flex justify-between items-center"
            onClick={() => setSelected((prev) => !prev)}
          >
            <p className="text-[#797979]">Choose an option</p>
            <DownArrow Selected={Selected} />
          </div>
          {Selected && (
            <div className="relative z-10 bg-[#171721]">
              <div className="bg-[#40404A] w-full h-[1px] my-2"></div>
              <div className="flex justify-end items-center">
                <button className="text-[#5587FD] text-base">
                  Deselect all
                </button>
              </div>
              <div className="flex flex-col gap-5">
                <CustomMultiCheckBox title="Query" />
                <CustomMultiCheckBox title="Response" />
                <CustomMultiCheckBox title="Score" />
                <CustomMultiCheckBox title="Query" />
                <CustomMultiCheckBox title="Response" />
                <CustomMultiCheckBox title="Score" />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const CustomSingleCheckBox = ({ title, isChecked, handleCheckboxChange }) => {
  return (
    <div className="flex gap-3 items-center">
      <input
        type="checkbox"
        checked={isChecked}
        onChange={handleCheckboxChange}
      />
      <label className="text-[#B6B6B9] font-medium">{title}</label>
    </div>
  );
};

const DurationSection = (props) => {
  return (
    <div className="mt-4">
      <SingleSelect
        title="Duration"
        selections={["Today", "Week", "Month", "All"]}
        selected={props.TimeFilter}
        OnClick={props.setTimeFilter}
        placeholder="Select a project"
      />
    </div>
  );
};

const ModelsSection = (props) => {
  return (
    <div className="mt-4">
      <SingleSelect
        title="Projects"
        selections={props.projectNames}
        selected={props.selectedProject}
        OnClick={props.handleProjectChange}
        placeholder="Select a project"
      />
    </div>
  );
};

const ColumnsSection = () => {
  return (
    <div className="mt-4">
      <MultiSelect title="Columns" />
    </div>
  );
};

const FilterSection = (props) => {
  return (
    <div className="mb-8">
      <h2 className="text-lg font-medium">Filter</h2>
      {props.duration && (
        <DurationSection
          TimeFilter={props.TimeFilter}
          setTimeFilter={props.setTimeFilter}
        />
      )}
      {props.projectNames && (
        <ModelsSection
          projectNames={props.projectNames}
          selectedProject={props.selectedProject}
          handleProjectChange={props.handleProjectChange}
        />
      )}
      {props.columns && <ColumnsSection />}
    </div>
  );
};

export default FilterSection;
