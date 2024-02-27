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
    <div className="bg-[#23232D] py-2.5 px-4 rounded-xl mb-4 ">
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
        />
      )}
      <AllLogsRowTop
        index={index}
        question={props.question}
        score={props.score}
        date={props.date}
        expand={expand}
        setExpand={setExpand}
        inModal={props.inModal}
      />
      {expand || props.inModal ? (
        <div className="w-[calc(100vw-640px)] overflow-auto">
          {props.score && (
            <>
              <Divider />
              <DataRow
                score
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
        </div>
      ) : (
        <></>
      )}
    </div>
  );
};

export default AllLogsRow;
