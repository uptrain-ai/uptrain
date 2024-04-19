"use client";
import React from "react";
import LineChart from "./LineChart";
import BarChart from "./BarChart";

const Chart = (props) => {
  return (
    <div className="p-5 bg-[#232331] rounded-xl  w-[calc(100vw-640px)]">
      {props.run_via === "schedule" ? (
        <LineChart
          selectedTab={props.selectedTab}
          projectData={props.projectData}
        />
      ) : (
        <BarChart
          selectedTab={props.selectedTab}
          projectData={props.projectData}
        />
      )}
    </div>
  );
};

const ChartSection = (props) => {
  return (
    <div className="mb-10 flex flex-col flex-1">
      <Chart
        TimeFilter={props.TimeFilter}
        run_via={props.run_via}
        selectedTab={props.selectedTab}
        projectData={props.projectData}
      />
    </div>
  );
};

export default ChartSection;