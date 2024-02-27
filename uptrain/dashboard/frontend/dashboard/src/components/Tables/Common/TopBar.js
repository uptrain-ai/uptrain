import React, { useState } from "react";

const CustomSelect = (props) => {
  const [selectedOption, setSelectedOption] = useState("");

  const handleSelectChange = (event) => {
    setSelectedOption(event.target.value);
  };

  return (
    <div className="rounded-xl bg-[#232331] px-6 py-2.5 text-[#B6B6B9] flex-1 max-w-[240px]">
      <select
        id="exampleSelect"
        value={selectedOption}
        onChange={handleSelectChange}
        className="w-full border-none bg-[#232331] text-sm"
      >
        <option value="">Choose row</option>
        <option value="option1">Choose an option</option>
        <option value="option2">Choose an option</option>
        <option value="option3">Choose an option</option>
      </select>
    </div>
  );
};

const TopBar = (props) => {
  return (
    <div className="bg-[#2B3962] py-2.5 px-4 rounded-xl mb-4">
      <div className="flex justify-between items-center gap-10">
        <p className=" text-sm font-medium text-[#B6B6B9]">
          Find the common topic among the selected row
        </p>
        <CustomSelect />
      </div>
    </div>
  );
};

export default TopBar;
