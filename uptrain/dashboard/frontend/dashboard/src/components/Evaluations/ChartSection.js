"use client";
import React from "react";
import LineChart from "./LineChart";
import BarChart from "./BarChart";

const Chart = (props) => {
  return (
    <div className="p-5 bg-[#232331] rounded-xl">
      {/* <div className="flex  items-center gap-2.5">
        <h3 className="text-[#5C5C66] text-xl font-medium">
          Completeness Score{" "}
          {props.TimeFilter == "0"
            ? "Today"
            : props.TimeFilter == "1"
            ? "this Week"
            : props.TimeFilter == "2"
            ? "this Month"
            : "All"}
          :
        </h3>
        <h3 className="text-[#EFEFEF] text-2xl font-medium">60%</h3>
      </div> */}
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
