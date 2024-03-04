"use client";
import Image from "next/image";
import Link from "next/link";
import React from "react";
import { usePathname } from "next/navigation";

const LinkElement = (props) => {
  const pathname = usePathname();

  return (
    <Link className="flex" href={props.href}>
      <div
        className={`w-3 rounded-r-md ${
          pathname == props.href && "bg-[#5587FD]"
        }`}
      ></div>
      <div className="mx-7 flex gap-4 items-center">
        {props.children}
        <p
          className={`font-medium text-lg ${
            pathname == props.href ? "text-[#D6D6D6]" : "text-[#6D6D75]"
          }`}
        >
          {props.title}
        </p>
      </div>
    </Link>
  );
};

const SideBar = () => {
  const pathname = usePathname();

  return (
    <div className="py-11 sticky top-0">
      <div className="mx-10 mb-10">
        <Link href="/">
          <Image
            src="/UptrainLogo.png"
            width={240}
            height={60}
            alt="Uptrain Logo"
            className="w-[120px] h-auto"
          />
        </Link>
      </div>
      <div className="flex flex-col gap-6">
        <LinkElement title="Home" href="/">
          {pathname == "/" ? (
            <Image
              src="/SideBar-Home-white.png"
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          ) : (
            <Image
              src="/SideBar-Home.png"
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          )}
        </LinkElement>
        <LinkElement title="Evaluations" href="/evaluations">
          {pathname == "/evaluations" ? (
            <Image
              src="/SideBar-Evaluations-white.png"
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          ) : (
            <Image
              src="/SideBar-Evaluations.png"
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          )}
        </LinkElement>
        <LinkElement title="Experiment" href="/experiment">
          {pathname == "/experiment" ? (
            <Image
              src="/SideBar-Experiment-white.png"
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          ) : (
            <Image
              src="/SideBar-Experiment.png"
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          )}
        </LinkElement>
        <LinkElement title="Prompts" href="/prompts">
          {pathname == "/prompts" ? (
            <Image
              src="/SideBar-prompts-white.png"
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          ) : (
            <Image
              src="/SideBar-prompts.png"
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          )}
        </LinkElement>
        <LinkElement title="API Keys" href="/api-keys">
          {pathname == "/api-keys" ? (
            <Image
              src="/SideBar-ApiKeys-white.png"
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          ) : (
            <Image
              src="/SideBar-ApiKeys.png"
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          )}
        </LinkElement>
        <LinkElement title="Contact Us" href="/contact-us">
          {pathname == "/contact-us" ? (
            <Image
              src="/SideBar-ContactUs-white.png"
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          ) : (
            <Image
              src="/SideBar-ContactUs.png"
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          )}
        </LinkElement>
      </div>
    </div>
  );
};

export default SideBar;
