import React, { useState } from "react";
import Step2OverModal from "./Step2OverModal";

const Step2 = (props) => {
  const [openModal, setOpenModal] = useState(false);
  const [selectedKey, setSelectedKey] = useState(null);

  return (
    <div>
      {openModal && (
        <Step2OverModal
          selectedKey={selectedKey}
          close={() => setOpenModal(false)}
          data={props.multiMetrics}
          metadata={props.metadata}
          setMetadata={props.setMetadata}
        />
      )}
      <h2 className="text-lg text-[#B0B0B1] font-medium mb-5">
        Select Metrics
      </h2>
      <form onSubmit={props.next}>
        <div className="grid grid-cols-2 bg-[#171721] rounded-xl p-8">
          {props.singleMetrics.map((item, index) => (
            <div className="mb-4" key={index}>
              <input
                type="checkbox"
                id={item}
                name={item}
                value="checked"
                checked={props.selectedChecks.includes(index)}
                onChange={() => {
                  const updatedSelectedChecks = [...props.selectedChecks];
                  if (updatedSelectedChecks.includes(index)) {
                    updatedSelectedChecks.splice(
                      updatedSelectedChecks.indexOf(index),
                      1
                    );
                  } else {
                    updatedSelectedChecks.push(index);
                  }
                  props.setselectedChecks(updatedSelectedChecks);
                }}
              />
              <label htmlFor={item} className="text-[#959393] px-2">
                {item}
              </label>
            </div>
          ))}
          {Object.entries(props.multiMetrics).map(([key, value], index) => (
            <div className="mb-4" key={index}>
              <input
                type="checkbox"
                id={key}
                name={key}
                value="checked"
                checked={props.selectedMultiChecks.includes(key)}
                onChange={() => {
                  const updatedSelectedChecks = [...props.selectedMultiChecks];
                  if (updatedSelectedChecks.includes(key)) {
                    updatedSelectedChecks.splice(
                      updatedSelectedChecks.indexOf(key),
                      1
                    );
                  } else {
                    setSelectedKey(key);
                    setOpenModal(true);
                    updatedSelectedChecks.push(key);
                  }
                  props.setSelectedMultiChecks(updatedSelectedChecks);
                }}
              />
              <label htmlFor={key} className="text-[#959393] px-2">
                {key}
              </label>
            </div>
          ))}
        </div>
        <div className="flex justify-end mt-5">
          <button
            type="Submit"
            className="bg-[#5587FD] text-white px-10 py-2.5 font-semibold text-lg rounded-xl"
            onClick={props.next}
          >
            Finish
          </button>
        </div>
      </form>
    </div>
  );
};

export default Step2;
