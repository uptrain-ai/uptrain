import React from "react";
import SingleSelect from "../DropDowns/SingleSelect";
import { usePathname, useRouter } from "next/navigation";

const PromptFilterSection = (props) => {
  const pathname = usePathname();
  const router = useRouter();

  const handlePromptChange = (index) => {
    let lastIndex = pathname.lastIndexOf("/");
    let result = pathname.substring(0, lastIndex) + "/" + props.prompts[index];
    router.push(result);
  };

  const index = props.prompts.indexOf(props.selectedPrompt);

  return (
    <div className="-mt-4">
      <SingleSelect
        title="Prompts"
        selections={props.prompts}
        selected={index}
        OnClick={handlePromptChange}
        placeholder="Select a project"
      />
    </div>
  );
};
export default PromptFilterSection;
