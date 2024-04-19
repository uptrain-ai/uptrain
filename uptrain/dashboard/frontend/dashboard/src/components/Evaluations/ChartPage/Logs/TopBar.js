import SpinningLoader from "@/components/UI/SpinningLoader";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import React, { useState } from "react";
import { useSelector } from "react-redux";

// const CustomSelect = (props) => {
//   const [selectedOption, setSelectedOption] = useState("");

//   const handleSelectChange = (event) => {
//     setSelectedOption(event.target.value);
//   };

//   return (
//     <div className="rounded-xl bg-[#232331] px-6 py-2.5 text-[#B6B6B9] flex-1 max-w-[240px]">
//       <select
//         id="exampleSelect"
//         value={selectedOption}
//         onChange={handleSelectChange}
//         className="w-full border-none bg-[#232331] text-sm"
//       >
//         <option value="">Choose row</option>
//         <option value="option1">Choose an option</option>
//         <option value="option2">Choose an option</option>
//         <option value="option3">Choose an option</option>
//       </select>
//     </div>
//   );
// };

const TopBar = (props) => {
  const [loading, setLoading] = useState(false);
  const [commonTopic, setCommonTopic] = useState(null);

  const uptrainAccessKey = useSelector(selectUptrainAccessKey);
  const questions =
    props.projectData[0] && props.projectData[0].map((item) => item.question);

  const score =
    props.projectData[0] &&
    props.projectData[0].map((item) => item[`score_${props.selectedTab}`]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);

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
        setLoading(false);
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
    <div className="bg-[#2B3962] py-2.5 px-4 rounded-xl mb-4">
      {commonTopic ? (
        loading ? (
          <SpinningLoader />
        ) : (
          <div className="flex gap-5 items-center">
            {" "}
            <p className="text-sm text-[#B6B6B9] max-w-lg text-center">
              The common topic is :
            </p>
            <p className="bg-[#232331] text-white text-sm py-2.5 px-7 rounded-xl disabled:opacity-20">
              {commonTopic}
            </p>
          </div>
        )
      ) : (
        <div className="flex justify-between items-center gap-10">
          <p className=" text-sm font-medium text-[#B6B6B9]">
            {/* Find the common topic among the selected row */}
            Get the common topic of questions with low scores
          </p>
          <button
            onClick={handleSubmit}
            className="bg-[#232331] text-white text-sm py-2.5 px-7 rounded-xl disabled:opacity-20"
          >
            Find Common Topic
          </button>
        </div>
      )}
    </div>
  );
};

export default TopBar;
