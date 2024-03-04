import Image from "next/image";
import React, { useState } from "react";
import InsightsModal from "./InsightsModal";

const InsightRow = (props) => {
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
  };

  return (
    <div
      className={`p-4 flex gap-2.5 text-[#B6B6B9] font-medium justify-between border  rounded-xl cursor-pointer ${
        isHovered ? "border-[#5587FD]" : "border-[#171721]"
      }`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className="flex gap-2.5 items-start">
        <p className="text-base pt-0.5">{props.number}</p>
        <div className="flex flex-col justify-start gap-3">
          <p className="text-lg">{props.title}</p>
          <div className="flex gap-2.5 items-center">
            <p>Score: {props.score}</p>
            {props.drop ? (
              <Image src="DownArrow.svg" alt="" width={11} height={11} />
            ) : (
              <Image src="UpArrow.svg" alt="" width={11} height={11} />
            )}
            <p>( {props.details} )</p>
          </div>
        </div>
      </div>
      <div className="flex flex-col items-end justify-between">
        <p className="text-[#4F4F56] text-base whitespace-nowrap">
          01-01-23, 02:36 AM
        </p>
        {isHovered ? (
          <Image src="./RightPointingArrowBlue.svg" width={18} height={18} />
        ) : (
          <></>
        )}
      </div>
    </div>
  );
};

const Insights = () => {
  const [RequestSent, setRequestSent] = useState(false);
  const [openInsightsModel, setOpenInsightsModel] = useState(false);

  const data = [
    {
      title: "Completeness drop noticed in “Summary_Expt_06”",
      score: "60%",
      drop: true,
      details: "8% drop compared to last week.",
      date: "01-01-23, 02:36 AM",
    },
    {
      title: "Completeness  drop noticed in “Summary_Expt_02”",
      score: "60%",
      drop: false,
      details: "6% hike compared to last week.",
      date: "01-01-23, 02:36 AM",
    },
    {
      title: "Completeness drop noticed in “Summary_Expt_06”",
      score: "60%",
      drop: true,
      details: "8% drop compared to last week.",
      date: "01-01-23, 02:36 AM",
    },
    {
      title: "Completeness drop noticed in “Summary_Expt_06”",
      score: "60%",
      drop: true,
      details: "8% drop compared to last week.",
      date: "01-01-23, 02:36 AM",
    },
  ];

  const handleRequest = () => {
    setRequestSent(true);
  };

  return (
    <div>
      {openInsightsModel && (
        <InsightsModal close={() => setOpenInsightsModel(false)} />
      )}
      <div className="flex items-center justify-center flex-col py-10">
        <p className="text-lg text-[#B6B6B9] max-w-lg text-center">
          {RequestSent
            ? "Your request has been sent, Someone from our team will connect with you soon!!"
            : "Gain access to exclusive insights ahead of the crowd"}
        </p>
        <button
          className="bg-[#5587FD] text-white text-base mt-5 py-2.5 px-7 rounded-xl disabled:opacity-20"
          onClick={handleRequest}
          disabled={RequestSent}
        >
          Request Early Access
        </button>
        <button
          className="text-sm text-[#4F4F56] mt-5"
          onClick={() => setOpenInsightsModel(true)}
        >
          Know more
        </button>
      </div>
      {/* {data.map((item, index) => (
        <InsightRow
          key={index}
          number={index + 1}
          title={item.title}
          score={item.score}
          drop={item.drop}
          details={item.details}
          date={item.date}
        />
      ))} */}
    </div>
  );
};

export default Insights;
