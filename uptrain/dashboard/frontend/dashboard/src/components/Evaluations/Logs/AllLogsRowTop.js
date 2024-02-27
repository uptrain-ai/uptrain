import { changeDateFormat } from "@/utils/changeDateFormat";
import Image from "next/image";
import React from "react";

const AllLogsRowTop = (props) => {
  const formattedDate = changeDateFormat(props.date);

  return (
    <div className="flex gap-4">
      <p className="text-[#B6B6B9] font-medium text-base">{props.index}</p>
      <div className="flex-1">
        <h3 className="text-[#B6B6B9] font-medium text-base pb-4">
          {props.question}
        </h3>
        <div className="flex justify-between">
          <div className="flex gap-3 items-center">
            <p className="font-medium text-base text-[#4F4F56]">
              {props.selectedTab} Score:{" "}
              <span className="text-lg text-[#F8F14A]">{props.score}</span>
            </p>
            <div className="h-4 w-[1px] bg-[#4F4F56] "></div>
            <p className="font-medium text-base text-[#4F4F56]">
              {formattedDate}
            </p>
          </div>
          {!props.inModal ? (
            <button onClick={() => props.setExpand((prev) => !prev)}>
              <Image
                src="/DropDownIcon.svg"
                height={5.5}
                width={11}
                className={`${
                  props.expand && "rotate-180"
                } transition-all delay-150`}
              />
            </button>
          ) : (
            <></>
          )}
        </div>
      </div>
    </div>
  );
};

export default AllLogsRowTop;
