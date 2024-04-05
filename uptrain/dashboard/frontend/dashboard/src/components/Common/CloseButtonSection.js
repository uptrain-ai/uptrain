import Image from "next/image";
import React from "react";

const CloseButtonSection = (props) => {
  return (
    <div className="flex justify-end">
      <button onClick={props.onClick}>
        <Image src={`${process.env.NEXT_PUBLIC_BASE_PATH}/Close.svg`} width={20} height={20} alt="Close Icon" />
      </button>
    </div>
  );
};
export default CloseButtonSection;
