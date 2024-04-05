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
        Created At: <span className="text-[#B6B6B9]">{formattedDate}</span>
      </p>
    </div>
  );
};

export default TextSection;
