import React from "react";
import TopBar from "../../Tables/Common/TopBar";
import AllLogsRow from "./AllLogsRow";

const AllLogs = (props) => {

  return (
    <div>
      {/* <TopBar /> */}
      {props.projectData[0] &&
        props.projectData[0].map((item, index) => (
          <AllLogsRow
            key={index}
            index={index}
            question={item.question}
            response={item.response}
            explanation={item[`explanation_${props.selectedTab}`]}
            score={item[`score_${props.selectedTab}`]}
            prompt_version={props.projectData[5]}
            data={item}
            model={props.projectData[6]}
          />
        ))}
    </div>
  );
};

export default AllLogs;
