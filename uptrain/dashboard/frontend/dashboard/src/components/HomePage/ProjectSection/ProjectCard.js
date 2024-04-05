import React, { useState } from "react";
import TextSection from "./TextSection";
import HeaderSection from "./HeaderSection";
import { useRouter } from "next/navigation";

const ProjectCard = (props) => {
  const [isHovered, setIsHovered] = useState(false);
  const router = useRouter();

  const originalTimestamp = props.date;
  const dateObj = new Date(originalTimestamp);
  const options = { year: "numeric", month: "short", day: "2-digit" };
  const formattedDate = dateObj
    .toLocaleDateString("en-US", options)
    .replace(",", "");

  const goToProjectpage = props.title && !props.title.includes("/");

  return (
    <button
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`${
        isHovered
          ? "bg-[#171721] border-[#5587FD]"
          : "bg-[#23232D] border-[#23232D]"
      } border p-4 rounded-xl text-left`}
      onClick={() => {
        router.push(
          props.projectType === "schedule"
            ? `/schedule/${props.projectId}`
            : props.projectType === "checkset"
            ? `/checkset/${props.projectId}`
            : `/evaluations/${goToProjectpage ? props.title : ""}`
        );
      }}
    >
      <HeaderSection title={goToProjectpage ? props.title : props.title && props.title.split("/").slice(0, -1).concat(" data").join("/")} />
      <TextSection
        timeStamp={formattedDate}
      />
    </button>
  );
};

export default ProjectCard;
