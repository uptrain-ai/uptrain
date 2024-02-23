import React from "react";
import AllLogsRow from "./AllLogsRow";
import TopBar from "../../Tables/Common/TopBar";

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
            question={item.data.question}
            response={item.data.response}
            item={item}
            timestamp={item.timestamp}
            selectedTab={props.selectedTab}
            explanation={item.checks[`explanation_${props.selectedTab}`]}
            score={item.checks[`score_${props.selectedTab}`]}
          />
        ))}
    </div>
  );
};

export default AllLogs;
