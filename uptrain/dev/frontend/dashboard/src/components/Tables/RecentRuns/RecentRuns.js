import Image from "next/image";
import React, { useState } from "react";

const RecentRunsRow = (props) => {
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
  };

  return (
    <div
      className={`p-4 flex gap-2.5 text-[#B6B6B9] font-medium border  rounded-xl cursor-pointer ${
        isHovered ? "border-[#5587FD]" : "border-[#171721]"
      }`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div>
        <p className="text-base pt-0.5">{props.number}</p>
      </div>
      <div className="flex-1">
        <h3 className="text-lg">{props.title}</h3>
        <div className="flex text-[#4F4F56] text-base items-center flex-wrap gap-x-4">
          <p className="flex items-center justify-center">
            Completeness:
            <span className="text-[#B6B6B9] ml-1"> {props.completeness}%</span>
          </p>
          <div className="h-4 w-[1px] bg-[#4F4F56]"></div>
          <p className="flex items-center justify-center">
            Relevancy:{" "}
            <span className="text-[#B6B6B9] ml-1"> {props.relevancy}%</span>
          </p>
          <div className="h-4 w-[1px] bg-[#4F4F56]"></div>
          <p className="flex items-center justify-center">
            Correctness:{" "}
            <span className="text-[#B6B6B9] ml-1"> {props.correctness}%</span>
          </p>
        </div>
      </div>
      <div className="flex flex-col items-end justify-between">
        <p className="text-[#4F4F56] text-base whitespace-nowrap">
          {props.date}
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

const RecentRuns = () => {
  const data = [
    {
      id: "01",
      title: "Summary_Expt_01",
      date: "01-01-23, 02:36 AM",
      completeness: "60",
      relevancy: "80",
      correctness: "100",
    },
    {
      id: "02",
      title: "Summary_Expt_02",
      date: "01-01-23, 02:36 AM",
      completeness: "60",
      relevancy: "80",
      correctness: "100",
    },
    {
      id: "03",
      title: "Summary_Expt_02",
      date: "01-01-23, 02:36 AM",
      completeness: "60",
      relevancy: "80",
      correctness: "100",
    },
  ];

  return (
    <div>
      {data.map((item, index) => (
        <RecentRunsRow
          key={index}
          number={index + 1}
          title={item.title}
          completeness={item.completeness}
          relevancy={item.relevancy}
          correctness={item.correctness}
          date={item.date}
        />
      ))}
    </div>
  );
};

export default RecentRuns;
