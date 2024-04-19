import { scoreColorCalculator } from "@/utils/scoreColorCalculator";
import React from "react";

const DataBox = (props) => {
  const wordsLimit = 50;

  let data = typeof props.data !== "string" ? String(props.data) : props.data;
  data = data === null ? "" : data;

  const truncateExplanation = (explanation) => {
    const words = explanation.split(" ");
    const truncatedWords = words.slice(0, wordsLimit);
    return truncatedWords.join(" ");
  };

  const truncatedExplanation = truncateExplanation(data);

  const wordsCount = data.split(" ").length;
  const shouldShowMoreButton = wordsCount > wordsLimit;

  return (
    <div className="w-[calc((100vw-800px)/2)] bg-[#202C4F] p-5">
      <p
        className="font-medium text-sm inline leading-tight whitespace-normal break-words"
        dangerouslySetInnerHTML={{
          __html: props.inModal ? props.data : truncatedExplanation,
        }}
        style={{
          color:
            typeof props.data !== "string"
              ? scoreColorCalculator(props.score)
              : "#B6B6B9",
        }}
      ></p>
      {!props.inModal && shouldShowMoreButton && (
        <button
          onClick={() => props.setShowFull((prev) => !prev)}
          className="text-blue-500 inline"
        >
          ...more
        </button>
      )}
    </div>
  );
};

const DataRow = (props) => {
  return (
    <>
      <div className={`flex gap-5 ${props.className} `}>
        <p className="text-sm font-medium text-[#4F4F56] min-w-[120px] whitespace-normal break-words">
          {props.title}
        </p>
        <div
          className={`flex gap-5 w-[calc((100vw-800px)/2*${props.data.length})] pb-5`}
        >
          {props.data &&
            props.data.map((item, index) => (
              <DataBox
                data={item}
                key={index}
                setShowFull={props.setShowFull}
                inModal={props.inModal}
              />
            ))}
        </div>
      </div>
    </>
  );
};

export default DataRow;
