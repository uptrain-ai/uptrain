import React from "react";

const HeaderSection = (props) => {
  return (
    <div className="flex justify-between items-start w-full mb-10 overflow-auto pb-1">
      <h3 className="text-[#EFEFEF] font-medium text-xl">{props.title}</h3>
    </div>
  );
};

export default HeaderSection;
