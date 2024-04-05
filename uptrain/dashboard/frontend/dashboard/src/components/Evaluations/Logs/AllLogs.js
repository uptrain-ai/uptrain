import React from "react";
import AllLogsRow from "./AllLogsRow";

const AllLogs = (props) => {
  return (
    <div>
      {/* <TopBar /> */}
      {props.projectData &&
        props.projectData[0] &&
        props.projectData[0].map((item, index) => (
          <AllLogsRow
            key={index}
            index={index}
            question={item.question}
            response={item.response}
            item={item}
            timestamp={props.projectData[1]}
            selectedTab={props.selectedTab}
            explanation={item[`explanation_${props.selectedTab}`]}
            score={item[`score_${props.selectedTab}`]}
            data={item}
            updated={item[`status_score_${props.selectedTab}`]}
            uuid={item["row_uuid"]}
            AiConfidence={item[`score_confidence_${props.selectedTab}`]}
            projectName={item.project}
          />
        ))}
    </div>
  );
};

export default AllLogs;
