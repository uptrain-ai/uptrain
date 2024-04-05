import {
  removeUserData,
  selectUptrainAccessKey,
} from "@/store/reducers/userInfo";
import Image from "next/image";
import React from "react";
import { useDispatch, useSelector } from "react-redux";

const FilterContainer = (props) => {
  const apiKey = useSelector(selectUptrainAccessKey);
  const dispatch = useDispatch();

  const handleLogout = () => {
    dispatch(removeUserData());
    localStorage.removeItem("uptrain-apiKey");
  };

  return (
    <div className="flex flex-col max-h-screen  sticky top-0">
      <div className="flex items-center justify-end gap-7 max-w-[300px] w-full my-10">
        <a href="https://github.com/uptrain-ai/uptrain" target="_blank">
          <Image
            src={`${process.env.NEXT_PUBLIC_BASE_PATH}/GitHub.svg`}
            width={18}
            height={18}
            alt=""
            className="w-auto h-auto"
          />
        </a>
        <a
          href="https://docs.uptrain.ai/getting-started/introduction"
          target="_blank"
        >
          <Image
            src={`${process.env.NEXT_PUBLIC_BASE_PATH}/Documents.svg`}
            width={18}
            height={18}
            alt=""
            className="w-auto h-auto"
          />
        </a>
        {apiKey !== "default" && (
          <button
            className="rounded py-1.5 px-3 bg-[#3D75F7] font-semibold text-white hover:bg-[#23232D]"
            onClick={handleLogout}
          >
            LogOut
          </button>
        )}
        {/* <Image
          src="/FileIcon.svg"
          width={18}
          height={18}
          alt=""
          className="w-auto h-auto"
        />
        <Image
          src="/QuestionIcon.svg"
          width={18}
          height={18}
          alt=""
          className="w-auto h-auto"
        />
        <Image
          src="/NotificationIcon.svg"
          width={18}
          height={18}
          alt=""
          className="w-auto h-auto"
        />
        <div className="flex gap-4">
          <div className="w-9 h-9 rounded-full bg-white"></div>
          <Image
            src="/DropDownIcon.svg"
            width={18}
            height={18}
            alt=""
            className="w-auto h-auto"
          />
        </div> */}
      </div>
      {props.show && (
        <div className="bg-[#23232D] text-[#5C5C66] rounded-xl p-4 w-[300px] mb-5 flex-1  overflow-auto">
          {props.children}
        </div>
      )}
    </div>
  );
};

export default FilterContainer;
