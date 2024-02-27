import React from "react";

const CustomTabButton = (props) => {
  return (
    <button
      className={`border-b-4  pb-2 flex-1 font-medium text-lg text-center min-w-[220px] overflow-hidden ${
        props.selected
          ? "border-[#5587FD] text-white"
          : "border-[#5C5C66] text-[#5C5C66]"
      }`}
      onClick={props.onClick}
    >
      <p className="px-2">{props.title}</p>
    </button>
  );
};

export default CustomTabButton;
