import React, { useState } from "react";
import AllLogsRowTop from "./AllLogsRowTop";
import Divider from "./Divider";
import DataRow from "./DataRow";
import DataModal from "./DataModal";
import LikeModal from "./LikeModal";

const AllLogsRow = (props) => {
  const [expand, setExpand] = useState(false);
  const [showFull, setShowFull] = useState(false);
  const [showLikeModal, setShowLikeModal] = useState(false);

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
          timestamp={props.timestamp}
          response={props.response}
          explanation={props.explanation}
          data={props.data}
          item={props.item}
          inModal
          updated={props.updated}
          uuid={props.uuid}
          AiConfidence={props.AiConfidence}
          projectName={props.projectName}
        />
      )}
      {showLikeModal && (
        <LikeModal
          onClick={() => setShowLikeModal(false)}
          uuid={props.uuid}
          selectedTab={props.selectedTab}
          score={props.score}
          projectName={props.projectName}
        />
      )}
      <AllLogsRowTop
        index={index}
        question={props.question}
        score={props.score}
        date={props.timestamp}
        expand={expand}
        setExpand={setExpand}
        inModal={props.inModal}
        selectedTab={props.selectedTab}
        setShowLikeModal={setShowLikeModal}
        updated={props.updated}
        uuid={props.uuid}
        projectName={props.projectName}
        AiConfidence={props.AiConfidence}
      />
      {expand || props.inModal ? (
        <>
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
                key !== "question"
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
        </>
      ) : (
        <></>
      )}
    </div>
  );
};

export default AllLogsRow;
