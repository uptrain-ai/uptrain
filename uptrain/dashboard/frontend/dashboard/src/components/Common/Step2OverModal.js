import React from "react";
import CloseButtonSection from "./CloseButtonSection";

const Step2OverModal = (props) => {
  const handleSubmit = (event) => {
    event.preventDefault();
    props.close();
  };
  
  return (
    <div className="fixed top-0 left-0 w-screen h-screen backdrop-blur flex items-center justify-center overflow-auto p-10 z-40">
      <div className="rounded-xl border-[#5587FD] bg-[#23232D] p-8 max-w-[70%] w-full max-h-[100%] overflow-auto">
        <CloseButtonSection onClick={props.close} />
        <h2 className="text-lg text-[#B0B0B1] font-medium mb-5">
          {props.selectedKey} values
        </h2>
        <form onSubmit={handleSubmit}>
          {props.data[props.selectedKey].map((item, index) => (
            <input
              key={index}
              className="bg-[#171721] rounded-xl px-6 py-4 text-[#B6B6B9] w-full mt-5"
              placeholder={item}
              required
              disabled={props.promptVersionName}
              value={
                props.metadata[props.selectedKey]
                  ? props.metadata[props.selectedKey][item]
                  : props.selectedKey[item]
              }
              onChange={(e) => {
                props.setMetadata({
                  ...props.metadata, // Removed square brackets from props.metadata
                  [props.selectedKey]: {
                    ...props.metadata[props.selectedKey], // Removed square brackets from props.metadata[props.selectedKey]
                    [item]: e.target.value,
                  },
                });
              }}
            />
          ))}
          <div className="flex justify-end mt-5">
            <button
              type="Submit"
              className="bg-[#5587FD] text-white px-10 py-2.5 font-semibold text-lg rounded-xl"
              onClick={props.next}
            >
              Next
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Step2OverModal;
