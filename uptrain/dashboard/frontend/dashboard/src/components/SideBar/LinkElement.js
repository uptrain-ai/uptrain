import Link from "next/link";
import { usePathname } from "next/navigation";
import React from "react";

const LinkElement = (props) => {
  const pathname = usePathname();

  return (
    <Link className="flex" href={props.href}>
      <div
        className={`w-3 rounded-r-md ${props.selected && "bg-[#5587FD]"}`}
      ></div>
      <div className="mx-7 flex gap-4 items-center">
        {props.children}
        <p
          className={`font-medium text-lg ${
            props.selected ? "text-[#D6D6D6]" : "text-[#6D6D75]"
          }`}
        >
          {props.title}
        </p>
      </div>
    </Link>
  );
};

export default LinkElement;
