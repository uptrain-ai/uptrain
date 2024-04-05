import React, { useState } from "react";
import InsightsModal from "./InsightsModal";
import { useSelector } from "react-redux";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";

const Insights = (props) => {
  const uptrainAccessKey = useSelector(selectUptrainAccessKey);
  const [openInsightsModel, setOpenInsightsModel] = useState(false);
  const [commonTopic, setCommonTopic] = useState("");

  const questions =
    props.projectData[0] &&
    props.projectData[0].map((item) => item.question);

  const score =
    props.projectData[0] &&
    props.projectData[0].map(
      (item) => item[`score_${props.selectedTab}`]
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
