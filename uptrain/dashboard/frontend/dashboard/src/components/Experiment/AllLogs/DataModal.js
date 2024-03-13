import React from "react";
import AllLogsRow from "./AllLogsRow";

const DataModal = (props) => {
  return (
    <div
      className="fixed top-0 left-0 w-screen h-screen backdrop-blur flex items-center justify-center overflow-auto p-10 z-10"
      onClick={props.onClick}
    >
      <div className="rounded-xl border-[#5587FD] bg-[#23232D] p-8 max-w-[70%] w-full max-h-[100%] overflow-auto">
        <AllLogsRow
          inModal
          index={props.index}
          question={props.question}
          score={props.score}
          date={props.date}
          response={props.response}
          explanation={props.explanation}
          prompt_version={props.prompt_version}
          data={props.data}
          model={props.model}
        />
      </div>
    </div>
  );
};

export default DataModal;
