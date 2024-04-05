import React, { useState } from "react";
import CustomTabButton from "../UI/CustomTabButton";

const ButtonSection = (props) => {
  const [data, setData] = useState(null);

  return (
    <div className="relative">
      <div className={`flex gap-5 mb-6 overflow-x-auto ${!props.prompt && "w-[calc(100vw-640px)]"} pb-5 scrollHorizontal`}>
        {props.tabs &&
          props.tabs.map((item, index) => (
            <CustomTabButton
              key={index}
              onClick={() => {
                props.setTab(index);
              }}
              title={item}
              selected={props.Tab == index}
              checks={props.checks}
              setData={setData}
            />
          ))}
      </div>
      {data ? (
        <div className="absolute z-10 top-11 left-10 rounded-xl border-[#5587FD] border bg-[#23232D] p-4 text-white  w-full overflow-auto">
          {Object.entries(data).map(([key, value]) => (
            <p>
              {key} : {value}
            </p>
          ))}
        </div>
      ) : (
        <></>
      )}
    </div>
  );
};

export default ButtonSection;
