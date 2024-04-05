"use client";
import Image from "next/image";
import Link from "next/link";
import React from "react";
import { usePathname } from "next/navigation";
import LinkElement from "./LinkElement";

const SideBar = () => {
  const pathname = usePathname();

  return (
    <div className="py-11 sticky top-0">
      <div className="mx-10 mb-10 flex gap-1">
        <Link href="/">
          <Image
            src={`${process.env.NEXT_PUBLIC_BASE_PATH}/UptrainLogo.png`}
            width={240}
            height={60}
            alt="Uptrain Logo"
            className="w-[120px] h-auto"
          />
        </Link>
        <Image
          src={`${process.env.NEXT_PUBLIC_BASE_PATH}/BetaButton.svg`}
          width={35}
          height={35}
          alt="Beta Button"
          className="w-[35px] h-auto"
        />
      </div>
      <div className="flex flex-col gap-6">
        <LinkElement title="Home" href="/" selected={pathname == "/"}>
          {pathname == "/" ? (
            <Image
              src={`${process.env.NEXT_PUBLIC_BASE_PATH}/SideBar-Home-white.png`}
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          ) : (
            <Image
              src={`${process.env.NEXT_PUBLIC_BASE_PATH}/SideBar-Home.png`}
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          )}
        </LinkElement>
        <LinkElement
          title="Evaluations"
          href="/evaluations"
          selected={pathname.includes("/evaluations")}
        >
          {pathname.includes("/evaluations") ? (
            <Image
              src={`${process.env.NEXT_PUBLIC_BASE_PATH}/SideBar-Evaluations-white.png`}
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          ) : (
            <Image
              src={`${process.env.NEXT_PUBLIC_BASE_PATH}/SideBar-Evaluations.png`}
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          )}
        </LinkElement>
        <LinkElement
          title="Experiment"
          href="/experiment"
          selected={pathname.includes("/experiment")}
        >
          {pathname.includes("/experiment") ? (
            <Image
              src={`${process.env.NEXT_PUBLIC_BASE_PATH}/SideBar-Experiment-white.png`}
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          ) : (
            <Image
              src={`${process.env.NEXT_PUBLIC_BASE_PATH}/SideBar-Experiment.png`}
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          )}
        </LinkElement>
        <LinkElement
          title="Prompts"
          href="/prompts"
          selected={pathname.includes("/prompts")}
        >
          {pathname.includes("/prompts") ? (
            <Image
              src={`${process.env.NEXT_PUBLIC_BASE_PATH}/SideBar-prompts-white.png`}
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          ) : (
            <Image
              src={`${process.env.NEXT_PUBLIC_BASE_PATH}/SideBar-prompts.png`}
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          )}
        </LinkElement>
        <LinkElement
          title="API Keys"
          href="/api-keys"
          selected={pathname == "/api-keys"}
        >
          {pathname == "/api-keys" ? (
            <Image
              src={`${process.env.NEXT_PUBLIC_BASE_PATH}/SideBar-ApiKeys-white.png`}
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          ) : (
            <Image
              src={`${process.env.NEXT_PUBLIC_BASE_PATH}/SideBar-ApiKeys.png`}
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          )}
        </LinkElement>
        <LinkElement
          title="Contact Us"
          href="/contact-us"
          selected={pathname == "/contact-us"}
        >
          {pathname == "/contact-us" ? (
            <Image
              src={`${process.env.NEXT_PUBLIC_BASE_PATH}/SideBar-ContactUs-white.png`}
              width={36}
              height={36}
              className="w-[18px] h-[18px]"
              alt="SideBar Logo"
            />
          ) : (
            <Image
              src={`${process.env.NEXT_PUBLIC_BASE_PATH}/SideBar-ContactUs.png`}
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
