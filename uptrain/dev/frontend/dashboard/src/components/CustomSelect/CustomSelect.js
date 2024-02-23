import React, { useState } from "react";

const CustomSelect = (props) => {
  const handleSelectChange = (event) => {
    props.setSelectedOption(event.target.value);
  };

  return (
    <div className="mt-4">
      {props.title && (
        <h3 className="font-medium text-sm mb-1">{props.title}</h3>
      )}
      <div
        className={`bg-[#171721] rounded-full px-2.5 py-1 text-[#B6B6B9] ${props.className}`}
      >
        <select
          id="exampleSelect"
          value={props.selectedOption}
          onChange={handleSelectChange}
          className="w-full border-none bg-transparent"
          required={props.required}
        >
          <option value="">
            {props.placeholder ? props.placeholder : "Choose an option"}
          </option>
          {props.options.map((item, index) => (
            <option value={item}>{item}</option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default CustomSelect;
