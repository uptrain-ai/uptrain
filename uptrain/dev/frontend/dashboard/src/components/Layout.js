"use client";
import React from "react";
import SideBar from "./SideBar/SideBar";
import Header from "./Header";
import Image from "next/image";
import KeyModal from "./KeyModal/KeyModal";
import { selectUptrainAccessKey } from "@/store/reducers/userInfo";
import { useSelector } from "react-redux";

const MainArea = (props) => {
  return (
    <>
      <Image
        src="/BackgroudDottedBoxTopLeft.png"
        width={250}
        height={350}
        className="fixed top-0 right-0 w-64 h-80 -z-10"
      ></Image>
      <Image
        src="/BackgroudDottedBoxTopLeft.png"
        width={250}
        height={350}
        className="fixed bottom-0 left-52 w-64 h-80 transform rotate-180 -z-10"
      ></Image>
      <Header heading={props.heading} project={props.project} />
      <div className="flex items-start">{props.children}</div>
    </>
  );
};

const Layout = (props) => {
  const uptrainAccessKey = useSelector(selectUptrainAccessKey);

  return (
    <div className="flex w-screen overflow-y-auto overflow-x-hidden relative">
      {!uptrainAccessKey && <KeyModal />}
      <SideBar />
      <div className="flex-1 relative h-screen mx-10">
        <MainArea heading={props.heading} project={props.project}>
          {props.children}
        </MainArea>
      </div>
    </div>
  );
};

export default Layout;
