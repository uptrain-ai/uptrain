import React from "react";

const TextSection = (props) => {
  const originalTimestamp = props.date;
  const dateObj = new Date(originalTimestamp);
  const options = { year: "numeric", month: "short", day: "2-digit" };
  const formattedDate = dateObj
    .toLocaleDateString("en-US", options)
    .replace(",", "");

  return (
    <div>
      <p className="text-[#4F4F56] font-medium text-base">
        Run via:{" "}
        <span
          className={`${
            props.run_via == "project"
              ? "text-[#1CD492]"
              : props.run_via == "schedule"
              ? "text-blue-400"
              : props.run_via == "checkset"
              ? "text-orange-400"
              : props.run_via === "prompt"
              ? "text-violet-400"
              : "text-[#F8F14A]"
          }`}
        >
          {props.run_via.charAt(0).toUpperCase() + props.run_via.slice(1)}
        </span>
      </p>
      <p className="text-[#4F4F56] font-medium text-base">
        Latest Run: <span className="text-[#B6B6B9]">{formattedDate}</span>
      </p>
    </div>
  );
};

export default TextSection;
