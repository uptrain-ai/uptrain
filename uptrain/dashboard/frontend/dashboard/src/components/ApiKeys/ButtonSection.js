import React from "react";
import TabButton from "./TabButton";
import Image from "next/image";

const ButtonSection = (props) => {
  return (
    <div className="flex justify-between mb-5">
      <div className="flex gap-5">
        <TabButton
          selected={props.tabs == 0}
          onClick={() => {
            props.setTabs(0);
          }}
          title="Log and Evaluate"
        />
        <TabButton
          selected={props.tabs == 1}
          onClick={() => {
            props.setTabs(1);
          }}
          title="Experiments"
        />
        <TabButton
          selected={props.tabs == 2}
          onClick={() => {
            props.setTabs(2);
          }}
          title="Open Source"
        />
      </div>
      <button onClick={props.onClick}>
        <Image src="/CopyIcon.svg" width={24} height={24} alt="copy icon" />
      </button>
    </div>
  );
};

export default ButtonSection;
