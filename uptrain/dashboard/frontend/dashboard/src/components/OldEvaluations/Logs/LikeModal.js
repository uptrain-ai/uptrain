import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import Image from "next/image";
import React from "react";
import { useSelector } from "react-redux";

const LikeModal = (props) => {
  var scores = [0, 0.5, 1];
  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  // // Loop from 0 to 1 with a step size of 0.1
  // for (var i = 0; i <= 1; i += 0.1) {
  //   // Round the number to avoid floating point precision issues
  //   var value = Math.round(i * 10) / 10;
  //   // Push the rounded value to the array
  //   scores.push(value);
  // }

  const likeHandler = async (score) => {
    props.onClick();

    try {
      const data = {
        row_uuid: props.uuid,
        check: props.selectedTab,
        project_name: props.projectName,
        human_score: score,
      };

      const response = await fetch(
        process.env.NEXT_PUBLIC_BACKEND_URL + `api/public/human_feedback`,
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
    <div className="fixed top-0 left-0 w-screen h-screen backdrop-blur flex items-center justify-center overflow-auto p-10 z-20">
      <div className="rounded-xl border-[#5587FD] border bg-[#23232D] p-8 max-w-[70%] w-full max-h-[100%] overflow-auto">
        <h2 className="text-xl text-[#DADADA] font-medium mb-14">
          Modify Score
        </h2>
        <div className="flex gap-3 mb-5">
          <p className="text-[#919191] font-medium text-lg">Shared Feedback:</p>
          <Image
            src={`${process.env.NEXT_PUBLIC_BASE_PATH}/ThumbsUp.svg`}
            width={28}
            height={28}
            alt=""
            className="rotate-180"
          />
          <Image
            src={`${process.env.NEXT_PUBLIC_BASE_PATH}/ThumbsUpLight.svg`}
            width={28}
            height={28}
            alt=""
          />
        </div>
        <div className="flex gap-3 mb-5">
          <p className="text-[#919191] font-medium text-lg">
            {props.selectedTab} Score:
          </p>
          <p className="font-medium text-lg text-[#F8F14A]">{props.score}</p>
        </div>
        <div>
          <p className="text-[#919191] font-medium text-lg mb-5">
            Select Score:
          </p>
          <div className="flex gap-3">
            {scores.map((item, index) => (
              <button
                className="bg-[#1B1B1B] w-12 h-12 rounded-xl text-[#D3D3D3] flex items-center justify-center"
                onClick={() => likeHandler(item)}
                key={index}
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LikeModal;
