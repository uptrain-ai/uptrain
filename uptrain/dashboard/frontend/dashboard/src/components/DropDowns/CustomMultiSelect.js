import React, { useEffect, useRef, useState } from "react";
import DownArrow from "./DownArrow";

const CustomMultiCheckBox = (props) => {
  return (
    <div className="flex gap-3 items-center">
      <input
        type="checkbox"
        checked={props.selected}
        onChange={props.onClick}
      />
      <label className="text-[#B6B6B9] font-medium">{props.title}</label>
    </div>
  );
};

const CustomMultiSelect = (props) => {
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setSelected(false);
      }
    };

    document.addEventListener("click", handleClickOutside);
    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, []);

  const [selected, setSelected] = useState(false);

  return (
    <div className="mt-4 cursor-pointer">
      {props.title && (
        <h3 className="font-medium text-sm mb-1">{props.title}</h3>
      )}
      <div className="relative"  ref={dropdownRef}>
        <div className="bg-[#171721] rounded-2xl px-2.5 py-1 ">
          <div
            className="flex justify-between items-center"
            onClick={() => setSelected((prev) => !prev)}
          >
            <p className={props.placeholder ? "text-white" : "text-[#797979]"}>
              {props.placeholder ? props.placeholder : "Choose an option"}
            </p>
            <DownArrow Selected={selected} />
          </div>
          {selected && (
            <div className="relative z-10 bg-[#171721] overflow-x-scroll">
              <div className="bg-[#40404A] w-full h-[1px] my-2"></div>
              {/* <div className="flex justify-end items-center">
                <button className="text-[#5587FD] text-base">
                  Deselect all
                </button>
              </div> */}
              <div className="flex flex-col gap-5">
                {props.selections &&
                  props.selections.map((item, index) => (
                    <CustomMultiCheckBox
                      title={item}
                      key={index}
                      onClick={() => props.onSelect(item)}
                      selected={props.selected && props.selected.includes(item)}
                    />
                  ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CustomMultiSelect;
