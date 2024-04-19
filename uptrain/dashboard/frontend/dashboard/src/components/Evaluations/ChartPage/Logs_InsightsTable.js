"use client";
import React, { useState } from "react";
import CustomTabButton from "../../UI/CustomTabButton";
import Image from "next/image";
import AllLogs from "./Logs/AllLogs";
// import Insights from "@/components/Experiment/ChartPage/Insights/Insights";
import Insights from "./Insights/Insights";
import { CSVLink } from "react-csv";

const CsvComponent = ({ data }) => {
  const headers = Object.keys(data[0]);

  const formattedData = data.map((item) => {
    const formattedItem = {};
    for (const key in item) {
      formattedItem[key] = JSON.stringify(item[key]).replace(/,/g, "\\,");
    }
    return formattedItem;
  });

  return (
    <CSVLink
      data={formattedData}
      headers={headers}
      filename={"data.csv"}
      enclosingCharacter={`"`}
    >
      <Image
        src={`${process.env.NEXT_PUBLIC_BASE_PATH}/DownloadButton.svg`}
        height={42}
        width={42}
        alt="Download Button"
        className="w-auto h-auto"
      />
    </CSVLink>
  );
};

const ButtonSection = (props) => {
  return (
    <div className="flex w-full mb-6 justify-between">
      <div className="flex gap-5 flex-wrap">
        <CustomTabButton
          onClick={() => {
            props.setTab(1);
          }}
          title="All Logs"
          selected={props.Tab == 1}
        />
        <CustomTabButton
          onClick={() => {
            props.setTab(2);
          }}
          title="Insights"
          selected={props.Tab == 2}
        />
      </div>
      <CsvComponent data={props.projectData[0]} />
    </div>
  );
};

const TableSection = (props) => {
  const [Tab, setTab] = useState(1);

  return (
    <div>
      <ButtonSection
        setTab={setTab}
        Tab={Tab}
        projectData={props.projectData}
      />
      {Tab == 1 ? (
        <AllLogs
          projectData={props.projectData}
          selectedTab={props.selectedTab}
          evaluationId={props.evaluationId}
        />
      ) : (
        <Insights
          projectData={props.projectData}
          selectedTab={props.selectedTab}
        />
      )}
    </div>
  );
};

export default TableSection;
