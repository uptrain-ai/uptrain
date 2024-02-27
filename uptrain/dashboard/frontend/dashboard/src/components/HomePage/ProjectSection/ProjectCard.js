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
      } border p-4 rounded-xl text-left`}
      onClick={() => {
        router.push(
          props.run_via === "experiment"
            ? `/experiment`
            : props.run_via === "prompt"
            ? `/prompts`
            : `/evaluations`
        );
      }}
    >
      <HeaderSection title={props.title} />
      <TextSection
        health={props.health}
        date={props.date}
        run_via={props.run_via}
      />
    </button>
  );
};

export default ProjectCard;
