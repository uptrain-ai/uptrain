import React from "react";

const DataBox = (props) => {
  const wordsLimit = 50;

  const truncateExplanation = (explanation) => {
    const words = explanation.split(" ");
    const truncatedWords = words.slice(0, wordsLimit);
    return truncatedWords.join(" ");
  };

  const truncatedExplanation = truncateExplanation(props.data);

  const wordsCount = props.data.split(" ").length;
  const shouldShowMoreButton = wordsCount > wordsLimit;

  return (
    <div className="w-[calc((100vw-780px)/2)] bg-[#202C4F] p-5">
      <p
        className="font-medium text-sm text-[#B6B6B9] inline leading-tight"
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
  );
};

const DataRow = (props) => {
  return (
    <>
      <div className={`flex gap-5 ${props.className} `}>
        <p className="text-sm font-medium text-[#4F4F56] min-w-[100px]">
          {props.title}
        </p>
        <div
          className={`flex gap-5 w-[calc((100vw-760px)/2*${props.data.length})] pb-5`}
        >
          {props.data.map((item, index) =>
            props.score ? (
              <div className="w-[calc((100vw-780px)/2)] bg-[#202C4F] p-5 text-yellow-500">
                <p>{item}</p>
              </div>
            ) : (
              <DataBox
                data={item}
                key={index}
                setShowFull={props.setShowFull}
                inModal={props.inModal}
              />
            )
          )}
          {props.data.map((item, index) =>
            props.score ? (
              <div className="w-[calc((100vw-780px)/2)] bg-[#202C4F] p-5 text-yellow-500">
                <p>{item}</p>
              </div>
            ) : (
              <DataBox
                data={item}
                key={index}
                setShowFull={props.setShowFull}
                inModal={props.inModal}
              />
            )
          )}
        </div>
      </div>
    </>
  );
};

export default DataRow;
