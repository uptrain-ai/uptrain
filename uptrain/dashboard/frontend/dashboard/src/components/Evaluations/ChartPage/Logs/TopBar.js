import Step2OverModal from "@/components/Common/Step2OverModal";
import SpinningLoader from "@/components/UI/SpinningLoader";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import React, { useState } from "react";
import { useSelector } from "react-redux";
import { models } from "@/utils/models";
import ModelSelector from "@/components/Common/ModelSelector";
import CloseButtonSection from "@/components/Common/CloseButtonSection";

const KeyModal = (props) => {
  const [openModal, setOpenModal] = useState(false);

  return (
    <div className="fixed top-0 left-0 w-screen h-screen backdrop-blur flex items-center justify-center overflow-auto p-10 z-40">
      <div className="rounded-xl border-[#5587FD] bg-[#23232D] p-8 max-w-[70%] w-full max-h-[100%] overflow-auto">
        <CloseButtonSection onClick={props.close} />
        <h2 className="text-lg text-[#B0B0B1] font-medium mb-5">
          {props.selectedKey} values
        </h2>
        {openModal && (
          <Step2OverModal
            selectedKey={props.selectedOption}
            close={() => setOpenModal(false)}
            data={props.models}
            metadata={props.metadata}
            setMetadata={props.setMetadata}
          />
        )}
        <form onSubmit={props.handleSubmit}>
          <ModelSelector
            selectedOption={props.selectedOption}
            models={props.models}
            metadata={props.metadata}
            setMetadata={props.setMetadata}
            setSelectedOption={props.setSelectedOption}
            setOpenModal={setOpenModal}
          />
          <div className="flex justify-end mt-5">
            <button
              type="Submit"
              className="bg-[#5587FD] text-white px-10 py-2.5 font-semibold text-lg rounded-xl"
            >
              Next
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const TopBar = (props) => {
  const [loading, setLoading] = useState(false);
  const [commonTopic, setCommonTopic] = useState(null);
  const [openKeyModal, setOpenKeyModal] = useState(false);

  const [metadata, setMetadata] = useState({});
  const [selectedOption, setSelectedOption] = useState("");

  const uptrainAccessKey = useSelector(selectUptrainAccessKey);
  const questions =
    props.projectData[0] && props.projectData[0].map((item) => item.question);

  const score =
    props.projectData[0] &&
    props.projectData[0].map((item) => item[`score_${props.selectedTab}`]);

  const handleSubmit = (event) => {
    event.preventDefault();
    setOpenKeyModal(false);
    SubmitData();
  };

  const SubmitData = async () => {
    setLoading(true);

    try {
      const data = {
        items: questions,
        scores: score,
        model: selectedOption,
        metadata: metadata,
      };

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
      {openKeyModal && (
        <KeyModal
          models={models}
          close={() => setOpenKeyModal(false)}
          metadata={metadata}
          setMetadata={setMetadata}
          selectedOption={selectedOption}
          setSelectedOption={setSelectedOption}
          handleSubmit={handleSubmit}
        />
      )}
      {commonTopic ? (
        loading ? (
          <SpinningLoader />
        ) : (
          <div className="flex gap-5 items-center">
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
            onClick={
              uptrainAccessKey == "default_key"
                ? () => {
                    setOpenKeyModal(1);
                  }
                : handleSubmit
            }
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
