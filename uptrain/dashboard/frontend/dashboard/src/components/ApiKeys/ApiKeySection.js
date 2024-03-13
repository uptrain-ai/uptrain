import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import React from "react";
import { useSelector } from "react-redux";
import GraySmallHeading from "../UI/GraySmallHeading";
import GrayParah18 from "../UI/GrayParah18";
import Image from "next/image";

const ApiKeySection = () => {
  const uptrainAccessKey = useSelector(selectUptrainAccessKey);
  const copyToClipboard = () => {
    navigator.clipboard.writeText(uptrainAccessKey);
  };

  return (
    <div className="mb-8">
      <GraySmallHeading>Your API Key</GraySmallHeading>
      <div className="gap-3 flex items-center">
        <div className="bg-[#171721] rounded-xl flex justify-between py-2.5 px-5 items-center mt-1.5 flex-1">
          <GrayParah18>{uptrainAccessKey}</GrayParah18>
          <button onClick={copyToClipboard}>
            <Image src="./CopyIcon.svg" width={18} height={18} alt="Copy Icon"/>
          </button>
        </div>
        {/* <button className="bg-transparent border-[#5587FD] border-2 rounded-xl px-5 py-3 font-medium text-sm text-[#5587FD] hover:bg-[#5587FD] hover:text-[#171721]">
            Revoke API Key
          </button> */}
      </div>
    </div>
  );
};

export default ApiKeySection;
