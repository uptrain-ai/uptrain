import { changeDateFormat } from "@/utils/changeDateFormat";
import Image from "next/image";
import React from "react";

const Row = (props) => {
  const colors = [
    "text-red-400",
    "text-yellow-400",
    "text-blue-400",
    "text-green-400",
  ];

  const formattedDate = changeDateFormat(props.data.timestamp[0]);

  return (
    <>
      <div className="flex justify-between mb-5">
        <div className="flex text-lg flex-wrap gap-x-5">
          <p className="text-[#4f4f56]">
            {props.data.prompt_name} | V{props.data.prompt_version}
          </p>
        </div>
        <p className="text-[#4f4f56] font-medium text-sm whitespace-nowrap">
          {formattedDate}
        </p>
      </div>
      <div>
        <p className="text-lg text-[#b6b6b9] mb-5">{props.data.prompt}</p>
        <div className="flex justify-between  gap-5 items-end">
          <div className="flex justify-between gap-x-5 gap-y-2 flex-wrap">
            {Object.entries(props.data.scores).map(([key, value], index) => (
              <p key={key} className="text-[#B9BDCE] text-sm">
                {key} :{" "}
                <span className={`${colors[index % 4]} font-bold`}>
                  {value}
                </span>
              </p>
            ))}
          </div>
          {!props.expanded && props.setExpand && (
            <button onClick={() => props.setExpand((prev) => !prev)}>
              <Image
                src="/DropDownIcon.svg"
                height={5.5}
                width={11}
                className={`${
                  props.expand && "rotate-180"
                } transition-all delay-150 min-w-[11px] w-auto h-auto`}
                alt="Drop-down Icon"
              />
            </button>
          )}
        </div>
      </div>
    </>
  );
};

export default Row;
