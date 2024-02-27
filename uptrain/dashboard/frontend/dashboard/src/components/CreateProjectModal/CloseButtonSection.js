import Image from "next/image";
import React from "react";

const CloseButtonSection = (props) => {
  return (
    <div className="flex justify-end">
      <button onClick={props.onClick}>
        <Image src="/Close.svg" width={20} height={20} alt="" />
      </button>
    </div>
  );
};
export default CloseButtonSection;
