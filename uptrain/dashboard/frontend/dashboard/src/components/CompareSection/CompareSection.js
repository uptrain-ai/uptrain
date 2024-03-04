import React from "react";
import SingleSelect from "../UI/SingleSelect";

const CompareSection = (props) => {
  const versions =
    props.selectedCompareProject != null &&
    props.filteredProjects[props.selectedCompareProject].prompts.map(
      (item) => item.prompt_version
    );

  return (
    <div>
      <h2 className="text-lg font-medium">Compare</h2>
      <div className="mt-4">
        <SingleSelect
          title="Project"
          selections={
            props.filteredProjects &&
            props.filteredProjects.map((item) => item.prompt_name)
          }
          placeholder="Select a prompt"
          selected={props.selectedCompareProject}
          OnClick={props.setSelectedCompareProject}
          UnSelect
        />
        {props.selectedCompareProject != null && (
          <>
            <div className="mt-4">
              <SingleSelect
                title="Select Version"
                placeholder="Select prompt version"
                selections={versions}
                selected={props.selectedVersion1}
                OnClick={props.setSelectedVersion1}
              />
            </div>
            <div className="mt-4">
              <SingleSelect
                title="Select Version"
                placeholder="Select prompt version"
                selections={versions}
                selected={props.selectedVersion2}
                OnClick={props.setSelectedVersion2}
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default CompareSection;
