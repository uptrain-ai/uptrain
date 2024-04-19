import { scoreColorCalculator } from "@/utils/scoreColorCalculator";
import React from "react";
import Image from "next/image";

const DataRow = (props) => {
  const wordsLimit = 80;

  let data = typeof props.data !== "string" ? String(props.data) : props.data;
  data = data === null ? "" : data;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(data);
  };

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
        <div>
          <p className="text-sm font-medium text-[#4F4F56] w-[120px] whitespace-normal break-words">
            {props.title}
          </p>
          <button className="mt-2" onClick={copyToClipboard}>
            <Image
              src={`${process.env.NEXT_PUBLIC_BASE_PATH}/CopyIcon.svg`}
              width={18}
              height={18}
              alt="Copy Icon"
            />
          </button>
        </div>
        <div className="flex-1">
          <p
            className="font-medium text-sm  inline"
            style={{
              color:
                typeof props.data !== "string"
                  ? scoreColorCalculator(props.score)
                  : "#B6B6B9",
            }}
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
