import React from "react";

const GrayParah18 = (props) => {
  return (
    <p className={`text-[#B6B6B9] text-lg font-medium ${props.className}`}>
      {props.children}
    </p>
  );
};

export default GrayParah18;
