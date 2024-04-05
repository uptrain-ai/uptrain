"use client";
import React from "react";
import SideBar from "./SideBar/SideBar";
import Header from "./Header";
import Image from "next/image";
import KeyModal from "./KeyModal/KeyModal";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import { useSelector } from "react-redux";
import FilterContainer from "./FilterContainer/FilterContainer";
import FilterSection from "./FilterSection/FilterSection";
import CompareSection from "./CompareSection/CompareSection";
import ProjectFilterSection from "./ProjectFilterSection/ProjectFilterSection";
import EvaluationsFilterSection from "./EvaluationsFilterSection/EvaluationsFilterSection";
import PromptFilterSection from "./PromptFilterSection/PromptFilterSection";

const MainArea = (props) => {
  return (
    <>
      <Image
        src={`${process.env.NEXT_PUBLIC_BASE_PATH}/BackgroudDottedBoxTopLeft.png`}
        width={250}
        height={350}
        className="fixed top-0 right-0 w-64 h-80 -z-10"
        alt=""
      ></Image>
      <Image
        src={`${process.env.NEXT_PUBLIC_BASE_PATH}/BackgroudDottedBoxTopLeft.png`}
        width={250}
        height={350}
        className="fixed bottom-0 left-52 w-64 h-80 transform rotate-180 -z-10"
        alt=""
      ></Image>
      <div className="flex gap-10 flex-1">
        <div className="flex-1 flex flex-col">
          <Header heading={props.heading} project={props.project} />
          <div className="flex items-start flex-1 gap-10 mb-5  w-[calc(100vw-640px)]">
            {props.children}
          </div>
        </div>
        <FilterContainer
          show={props.duration || props.compare || props.setProjectFilters}
        >
          <FilterSection
            TimeFilter={props.TimeFilter}
            setTimeFilter={props.setTimeFilter}
            duration={props.duration}
            projectNames={props.projectNames}
            selectedProject={props.selectedProject}
            handleProjectChange={props.handleProjectChange}
          />
          {props.evaluations && (
            <EvaluationsFilterSection
              evaluations={props.evaluations}
              evaluationId={props.evaluationId}
              prompt={props.prompt}
            />
          )}
          {props.prompts && (
            <PromptFilterSection
              prompts={props.prompts}
              selectedPrompt={props.selectedPrompt}
            />
          )}
          {props.setProjectFilters && (
            <ProjectFilterSection
              setProjectFilters={props.setProjectFilters}
              projectData={props.projectData}
              selectedTab={props.selectedTab}
              projectFilters={props.projectFilters}
            />
          )}
          {props.compare && (
            <CompareSection
              compare={props.compare}
              projectData={props.projectData}
            />
          )}
        </FilterContainer>
      </div>
    </>
  );
};

const Layout = (props) => {
  const uptrainAccessKey = useSelector(selectUptrainAccessKey);
  return (
    <div className="flex w-screen overflow-y-auto overflow-x-hidden relative">
      {!uptrainAccessKey && <KeyModal />}
      <SideBar />
      <div className="flex-1 relative h-screen mx-10 flex flex-col">
        <MainArea
          heading={props.heading}
          project={props.project}
          TimeFilter={props.TimeFilter}
          setTimeFilter={props.setTimeFilter}
          duration={props.duration}
          projectNames={props.projectNames}
          selectedProject={props.selectedProject}
          handleProjectChange={props.handleProjectChange}
          setProjectFilters={props.setProjectFilters}
          selectedTab={props.selectedTab}
          projectFilters={props.projectFilters}
          evaluations={props.evaluations}
          evaluationId={props.evaluationId}
          prompts={props.prompts}
          selectedPrompt={props.selectedPrompt}
          compare={props.compare}
          projectData={props.projectData}
        >
          {props.children}
        </MainArea>
      </div>
    </div>
  );
};

export default Layout;
