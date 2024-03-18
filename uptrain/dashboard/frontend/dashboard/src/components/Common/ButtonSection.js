import React from "react";
import CustomTabButton from "../UI/CustomTabButton";

const ButtonSection = (props) => {
  return (
    <div className="flex gap-5 mb-6 overflow-auto w-[calc(100vw-640px)] pb-5 scrollHorizontal">
      {props.tabs &&
        props.tabs.map((item, index) => (
          <CustomTabButton
            key={index}
            onClick={() => {
              props.setTab(index);
            }}
            title={item}
            selected={props.Tab == index}
          />
        ))}
    </div>
  );
};

export default ButtonSection;
