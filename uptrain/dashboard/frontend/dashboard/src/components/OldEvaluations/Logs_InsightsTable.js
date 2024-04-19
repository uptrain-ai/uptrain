"use client";
import React, { useState } from "react";
import CustomTabButton from "../UI/CustomTabButton";
import Image from "next/image";
import AllLogs from "./Logs/AllLogs";
import Insights from "../Evaluations/ChartPage/Insights/Insights";

const ButtonSection = (props) => {
  return (
    <div className="flex mb-6 justify-between">
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
      <button>
        <Image
          src={`${process.env.NEXT_PUBLIC_BASE_PATH}/DownloadButton.svg`}
          height={42}
          width={42}
          alt="Download Button"
          className="w-auto h-auto"
        />
      </button>
    </div>
  );
};

const TableSection = (props) => {
  const [Tab, setTab] = useState(1);

  return (
    <div>
      <ButtonSection setTab={setTab} Tab={Tab} />
      {Tab == 1 ? (
        <AllLogs
          projectData={props.projectData}
          selectedTab={props.selectedTab}
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
