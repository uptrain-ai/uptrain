import { scoreColorCalculator } from "@/utils/scoreColorCalculator";
import Image from "next/image";
import React from "react";

const AllLogsRowTop = (props) => {
  return (
    <div className="flex gap-4">
      <p className="text-[#B6B6B9] font-medium text-base">{props.index}</p>
      <div className="flex-1">
        <h3 className="text-[#B6B6B9] font-medium text-base pb-4">
          {props.question}
        </h3>
        <div className="flex justify-between">
          <div className="flex gap-3 items-center">
            {props.model.map((item, index) => (
              <p className="font-medium text-base text-[#4F4F56]" key={index}>
                {item} Score:{" "}
                <span
                  className="text-lg"
                  style={{
                    color: scoreColorCalculator(props.score[index]),
                  }}
                >
                  {props.score[index]}
                </span>
              </p>
            ))}
          </div>
          {!props.inModal ? (
            <button onClick={() => props.setExpand((prev) => !prev)}>
              <Image
                src={`${process.env.NEXT_PUBLIC_BASE_PATH}/DropDownIcon.svg`}
                height={5.5}
                width={11}
                className={`${
                  props.expand && "rotate-180"
                } transition-all delay-150 w-auto h-auto`}
                alt="Drop Down Icon"
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
