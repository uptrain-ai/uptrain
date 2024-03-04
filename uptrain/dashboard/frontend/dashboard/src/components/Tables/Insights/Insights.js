import Image from "next/image";
import React, { useState } from "react";
import InsightsModal from "./InsightsModal";
import { useSelector } from "react-redux";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";

const InsightRow = (props) => {
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
  };

  return (
    <div
      className={`p-4 flex gap-2.5 text-[#B6B6B9] font-medium justify-between border  rounded-xl cursor-pointer ${
        isHovered ? "border-[#5587FD]" : "border-[#171721]"
      }`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className="flex gap-2.5 items-start">
        <p className="text-base pt-0.5">{props.number}</p>
        <div className="flex flex-col justify-start gap-3">
          <p className="text-lg">{props.title}</p>
          <div className="flex gap-2.5 items-center">
            <p>Score: {props.score}</p>
            {props.drop ? (
              <Image src="DownArrow.svg" alt="" width={11} height={11} />
            ) : (
              <Image src="UpArrow.svg" alt="" width={11} height={11} />
            )}
            <p>( {props.details} )</p>
          </div>
        </div>
      </div>
      <div className="flex flex-col items-end justify-between">
        <p className="text-[#4F4F56] text-base whitespace-nowrap">
          01-01-23, 02:36 AM
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

const Insights = (props) => {
  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  // const [RequestSent, setRequestSent] = useState(false);
  const [openInsightsModel, setOpenInsightsModel] = useState(false);
  const [commonTopic, setCommonTopic] = useState("");

  const questions =
    props.projectData[0] &&
    props.projectData[0].map((item, index) => item.data.question);

  const score =
    props.projectData[0] &&
    props.projectData[0].map(
      (item, index) => item.checks[`score_${props.selectedTab}`]
    );

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      const data = { items: questions, scores: score };

      const response = await fetch(
        process.env.NEXT_PUBLIC_BACKEND_URL + `api/public/find_common_topic`,
        {
          method: "POST",
          headers: {
            "uptrain-access-token": `${uptrainAccessKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        }
      );

      if (response.ok) {
        const responseData = await response.json();
        setCommonTopic(responseData.common_topic);
      } else {
        console.error("Failed to submit:", response.statusText);
        // Handle error cases
      }
    } catch (error) {
      console.error("Error submitting:", error.message);
      // Handle network errors or other exceptions
    }
  };

  return (
    <div>
      {openInsightsModel && (
        <InsightsModal close={() => setOpenInsightsModel(false)} />
      )}
      <div className="flex items-center justify-center flex-col py-10">
        {commonTopic.length === 0 ? (
          <>
            <p className="text-lg text-[#B6B6B9] max-w-lg text-center">
              Get the common topic of questions with low scores
            </p>
            <button
              className="bg-[#5587FD] text-white text-base mt-5 py-2.5 px-7 rounded-xl disabled:opacity-20"
              onClick={handleSubmit}
            >
              Find Common Topic
            </button>
          </>
        ) : (
          <>
            <p className="text-lg text-[#B6B6B9] max-w-lg text-center">
              The common topic is :
            </p>
            <p className="text-lg text-[#B6B6B9] max-w-lg text-center">
              {commonTopic}
            </p>
          </>
        )}
        {/* <button
          className="text-sm text-[#4F4F56] mt-5"
          onClick={() => setOpenInsightsModel(true)}
        >
          Know more
        </button> */}
      </div>
      {/* {data.map((item, index) => (
        <InsightRow
          key={index}
          number={index + 1}
          title={item.title}
          score={item.score}
          drop={item.drop}
          details={item.details}
          date={item.date}
        />
      ))} */}
    </div>
  );
};

export default Insights;
