import React from "react";
import GraySmallHeading from "../UI/GraySmallHeading";
import GrayParah18 from "../UI/GrayParah18";
import { useSelector } from "react-redux";
import {
  selectTotalCredits,
  selectUsedCredits,
} from "@/store/reducers/userInfo";

const CreditsSection = () => {
  const totalCredits = useSelector(selectTotalCredits);
  const usedCredits = useSelector(selectUsedCredits);

  return (
    <div className="mb-8">
      <GraySmallHeading>Credits left</GraySmallHeading>
      <GrayParah18 className="mt-1.5">
        {usedCredits}
        <span className="text-[#4F4F56]">/{totalCredits}</span>
      </GrayParah18>
    </div>
  );
};

export default CreditsSection;
