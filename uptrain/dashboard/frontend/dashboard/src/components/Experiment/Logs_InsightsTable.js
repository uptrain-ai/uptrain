"use client";
import React, { useState } from "react";
import CustomTabButton from "../UI/CustomTabButton";
import Image from "next/image";
import AllLogs from "./AllLogs/AllLogs_Experiment";
import Insights from "./Insights/Insights";

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
      <button>
        <Image src="/DownloadButton.svg" height={42} width={42} />
      </button>
    </div>
  );
};

const TableSection = (props) => {
  const [Tab, setTab] = useState(1);

  return (
    <div className="mb-10">
      <ButtonSection setTab={setTab} Tab={Tab} />
      {Tab == 1 ? (
        <AllLogs
          projectData={props.projectData}
          selectedTab={props.selectedTab}
        />
      ) : (
        <Insights />
      )}
    </div>
  );
};

export default TableSection;
