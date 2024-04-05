import ChartPage from "@/components/Experiment/ChartPage/ChartPage";
import ProjectPage from "@/components/Experiment/Homepage/ProjectPage";
import React from "react";

const page = ({ params: { slug } }) => {
  return (
    <>
      {slug.length == 2 && <ChartPage slug={slug} />}
      {slug.length == 1 && <ProjectPage slug={slug} />}
    </>
  );
};

export default page;
