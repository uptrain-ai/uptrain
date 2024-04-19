import React, { useState } from "react";
import AllLogsRowTop from "./AllLogsRowTop";
import Divider from "./Divider";
import DataRow from "./DataRow";
import DataModal from "./DataModal";

const AllLogsRow = (props) => {
  const [expand, setExpand] = useState(false);
  const [showFull, setShowFull] = useState(false);

  let index =
    typeof props.index !== "string" ? String(props.index + 1) : props.index;
  if (index.length === 1) {
    index = "0" + index;
  }

  return (
    <div
      className="bg-[#23232D] py-2.5 px-4 rounded-xl mb-4 border border-[#23232D] hover:bg-[#171721] hover:border-[#5587fd]"
      onClick={() => {
        !expand && setExpand(true);
      }}
    >
      {!props.inModal && showFull && (
        <DataModal
          onClick={() => setShowFull(!showFull)}
          index={index}
          question={props.question}
          score={props.score}
          date={props.date}
          response={props.response}
          explanation={props.explanation}
          inModal
          prompt_version={props.prompt_version}
          data={props.data}
          model={props.model}
        />
      )}
      <AllLogsRowTop
        index={index}
        question={props.question}
        score={props.score}
        date={props.date}
        model={props.prompt_version}
        expand={expand}
        setExpand={setExpand}
        inModal={props.inModal}
      />
      {expand || props.inModal ? (
        <div className="w-[calc(100vw-672px)] overflow-auto">
          {props.prompt_version && (
            <>
              <Divider />
              <DataRow
                data={props.prompt_version}
                title={props.model}
                setShowFull={setShowFull}
                inModal={props.inModal}
              />
            </>
          )}
          {props.score && (
            <>
              <Divider />
              <DataRow
                data={props.score}
                title="Score"
                setShowFull={setShowFull}
                inModal={props.inModal}
              />
            </>
          )}
          {props.response && (
            <>
              <Divider />
              <DataRow
                data={props.response}
                title="Response"
                setShowFull={setShowFull}
                inModal={props.inModal}
              />
            </>
          )}
          {props.explanation && (
            <>
              <Divider />
              <DataRow
                data={props.explanation}
                title="Explanation"
                className="mb-5"
                setShowFull={setShowFull}
                inModal={props.inModal}
              />
            </>
          )}
          {Object.entries(props.data)
            .filter(
              ([key, value]) =>
                key !== "response" &&
                key !== "explanation" &&
                key !== "question" &&
                key !== "uptrain_experiment_columns" &&
                key !== props.model
            )
            .map(([key, value], index) => (
              <div key={index}>
                <Divider />
                <DataRow
                  data={value}
                  title={key}
                  className="mb-5"
                  setShowFull={setShowFull}
                  inModal={props.inModal}
                />
              </div>
            ))}
        </div>
      ) : (
        <></>
      )}
    </div>
  );
};

export default AllLogsRow;
