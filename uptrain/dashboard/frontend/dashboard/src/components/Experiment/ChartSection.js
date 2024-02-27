"use client";
import React from "react";
import BarChart from "./BarChart";

const Chart = (props) => {
  return (
    <div className="p-5 bg-[#232331] rounded-xl">
      {/* <div className="flex  items-center gap-2.5  mb-10">
        <h3 className="text-[#5C5C66] text-xl font-medium">
          Experimentation running{" "}
          {props.TimeFilter == "1"
            ? "Today"
            : props.TimeFilter == "2"
            ? "this Week"
            : "this Month"}
          :
        </h3>
        <h3 className="text-[#EFEFEF] text-2xl font-medium">60%</h3>
      </div> */}
      {props.projectData[7] && (
        <BarChart
          data={props.projectData[7]}
          selectedTab={props.selectedTab}
          chartKey={props.projectData[6]}
        />
      )}
    </div>
  );
};

const ChartSection = (props) => {
  return (
    <div className="mb-10">
      <Chart
        TimeFilter={props.TimeFilter}
        projectData={props.projectData}
        selectedTab={props.selectedTab}
      />
    </div>
  );
};

export default ChartSection;
