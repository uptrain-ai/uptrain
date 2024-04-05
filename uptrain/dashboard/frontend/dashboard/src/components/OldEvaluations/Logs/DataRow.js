import React from "react";

const DataRow = (props) => {
  const wordsLimit = 80;

  let data = typeof props.data !== "string" ?  String(props.data) : props.data;
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
    <>
      <div className={`flex gap-5 ${props.className}`}>
        <p className="text-sm font-medium text-[#4F4F56] min-w-[100px]">
          {props.title}
        </p>
        <div>
          <p
            className="font-medium text-sm text-[#B6B6B9] inline"
            dangerouslySetInnerHTML={{
              __html: props.inModal ? props.data : truncatedExplanation,
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
      </div>
    </>
  );
};

export default DataRow;