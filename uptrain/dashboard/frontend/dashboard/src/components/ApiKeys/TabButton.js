import React from "react";

const TabButton = (props) => {
  return (
    <button
      className={`font-medium border-b-2 px-3 pb-1  ${
        props.selected
          ? "text-[#F0F0F8] border-[#5587FD]"
          : "text-[#5C5C66] border-[#5C5C66]"
      }`}
      onClick={props.onClick}
    >
      <p>{props.title}</p>
    </button>
  );
};

export default TabButton;
