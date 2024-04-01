import React from "react";

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

export default CustomSingleCheckBox;
