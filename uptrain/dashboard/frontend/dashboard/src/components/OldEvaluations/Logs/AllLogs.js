import React from "react";
import AllLogsRow from "./AllLogsRow";

const AllLogs = (props) => {
  return (
    <div className="w-[calc(100vw-640px)]">
      {/* <TopBar /> */}
      {props.projectData &&
        props.projectData[0] &&
        props.projectData[0].map((item, index) => (
          <AllLogsRow
            key={index}
            index={item.id}
            question={item.data.question}
            response={item.data.response}
            item={item}
            timestamp={item.timestamp}
            selectedTab={props.selectedTab}
            explanation={item.checks[`explanation_${props.selectedTab}`]}
            score={item.checks[`score_${props.selectedTab}`]}
            data={item.data}
            updated={item.metadata && item.metadata[`score_${props.selectedTab}`]}
            uuid={item.metadata && item.metadata["row_uuid"]}
            AiConfidence={item.metadata && item.metadata[`score_confidence_${props.selectedTab}`]}
            projectName={item.project}
          />
        ))}
    </div>
  );
};

export default AllLogs;