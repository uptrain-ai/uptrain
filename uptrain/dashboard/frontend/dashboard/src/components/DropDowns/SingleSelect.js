import React, { useState, useRef, useEffect } from "react";
import DownArrow from "./DownArrow";
import CustomSingleCheckBox from "./CustomSingleCheckBox";

const SingleSelect = (props) => {
  const [selected, setSelected] = useState(false);
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

  return (
    <div className="mt-4">
      {props.title && (
        <h3 className="font-medium text-sm mb-1">{props.title}</h3>
      )}
      <div className="relative" ref={dropdownRef}>
        <div className="bg-[#171721] rounded-2xl px-2.5 py-1 overflow-auto cursor-pointer">
          <div
            className="flex justify-between items-center"
            onClick={() => setSelected((prev) => !prev)}
          >
            <p className="text-[#F5F5F5]">
              {props.selections && props.selections[props.selected]
                ? `${props.prelable != undefined ? props.prelable : ""} ${
                    props.selections[props.selected]
                  }`
                : props.placeholder}
            </p>
            <DownArrow Selected={selected} />
          </div>
          {selected && (
            <div className="relative bg-[#171721]  z-20">
              <div className="bg-[#40404A] w-full h-[1px] my-2"></div>
              <div className="flex flex-col gap-5">
                {props.selections &&
                  props.selections.map((item, index) => (
                    <CustomSingleCheckBox
                      title={item}
                      key={index}
                      isChecked={index === props.selected}
                      handleCheckboxChange={
                        props.UnSelect
                          ? index === props.selected
                            ? () => props.OnClick(null)
                            : () => props.OnClick(index)
                          : () => props.OnClick(index)
                      }
                      prelable={props.prelable}
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

export default SingleSelect;
