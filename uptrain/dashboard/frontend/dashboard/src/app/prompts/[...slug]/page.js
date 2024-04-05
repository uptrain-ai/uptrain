
import ProjectPage from "@/components/Prompts/Homepage/ProjectPage";
import PromptsPage from "@/components/Prompts/PromptsPage";
import React from "react";

const page = ({ params: { slug } }) => {
  return (
    <>
      {slug.length == 2 && <PromptsPage slug={slug} />}
      {slug.length == 1 && <ProjectPage slug={slug} />}
    </>
  );
};

export default page;
