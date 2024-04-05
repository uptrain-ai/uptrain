import React from "react";
import SingleSelect from "../DropDowns/SingleSelect";
import { usePathname, useRouter } from "next/navigation";

function getIndexByEvaluationId(array, id) {
  for (let i = 0; i < array.length; i++) {
    if (array[i].evaluation_id === id) {
      return i; // Return the index if found
    }
  }
  return -1; // Return -1 if not found
}

const EvaluationsFilterSection = (props) => {
  const pathname = usePathname();
  const router = useRouter();

  const index = getIndexByEvaluationId(props.evaluations, props.evaluationId);

  const handleEvaluationChange = (index) => {
    let lastIndex = pathname.lastIndexOf("/");
    let result =
      pathname.substring(0, lastIndex) +
      "/" +
      props.evaluations[index].evaluation_name;
    router.push(result);
  };

  return (
    <div className="-mt-4">
      <SingleSelect
        title="Evaluation"
        selections={props.evaluations.map((item) => item.evaluation_name)}
        selected={index}
        OnClick={handleEvaluationChange}
        placeholder="Select a evaluation"
      />
    </div>
  );
};
export default EvaluationsFilterSection;
