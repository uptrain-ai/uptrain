"use client";
import React, { useState } from "react";
import TextSection from "./TextSection";
import HeaderSection from "./HeaderSection";
import { useRouter } from "next/navigation";

const ProjectCard = (props) => {
  const [isHovered, setIsHovered] = useState(false);
  const router = useRouter();

  return (
    <button
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`${
        isHovered
          ? "bg-[#171721] border-[#5587FD]"
          : "bg-[#23232D] border-[#23232D]"
      } border p-4 rounded-xl text-left flex flex-col justify-between min-h-[150px]`}
      onClick={() => {
        router.push(`/evaluations/${props.project}/${props.evaluation}`);
      }}
    >
      <HeaderSection title={props.title} />
      <TextSection date={props.date} />
    </button>
  );
};

export default ProjectCard;
