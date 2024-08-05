"use client";

import React, { useEffect } from "react";
import { observer } from "mobx-react";
import { Loader, setToast, TOAST_TYPE } from "@plane/ui";
// plane web components
import { IssueAdditionalPropertyValues } from "@/plane-web/components/issue-types";
// plane web hooks
import { useIssueType, useIssueTypes } from "@/plane-web/hooks/store";
// plane web services
import { IssuePropertyValuesService } from "@/plane-web/services/issue-types";

type TIssueAdditionalPropertyValuesUpdateProps = {
  issueId: string;
  issueTypeId: string;
  projectId: string;
  workspaceSlug: string;
};

const issuePropertyValuesService = new IssuePropertyValuesService();

export const IssueAdditionalPropertyValuesUpdate: React.FC<TIssueAdditionalPropertyValuesUpdateProps> = observer((props) => {
  const { issueId, issueTypeId, projectId, workspaceSlug } = props;
  // states
  const [issuePropertyValues, setIssuePropertyValues] = React.useState({});
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  // store hooks
  const { getProjectIssueTypeLoader, getAllTypesPropertiesOptions } = useIssueTypes();
  const issueType = useIssueType(issueTypeId);
  // derived values
  const issueTypeDetails = issueType?.asJSON;
  const activeProperties = issueType?.activeProperties;
  const issueTypeLoader = getProjectIssueTypeLoader(projectId);

  // fetch issue custom property values
  useEffect(() => {
    async function fetchIssuePropertyValues() {
      setIsLoading(true);
      // This is required when accessing the peek overview from workspace level.
      await getAllTypesPropertiesOptions(workspaceSlug, projectId);
      await issuePropertyValuesService
        .fetchAll(workspaceSlug, projectId, issueId)
        .then((data) => {
          setIssuePropertyValues(data);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
    fetchIssuePropertyValues();
  }, [getAllTypesPropertiesOptions, issueId, projectId, workspaceSlug]);

  const handlePropertyValueChange = async (propertyId: string, value: string[]) => {
    setIssuePropertyValues((prev) => ({
      ...prev,
      [propertyId]: value,
    }));
    await issuePropertyValuesService
      .createUpdate(workspaceSlug, projectId, issueId, {
        [propertyId]: value,
      })
      .then(() => {
        // TODO: remove
        setToast({
          type: TOAST_TYPE.SUCCESS,
          title: "Success!",
          message: "Custom properties update successfully.",
        });
      })
      .catch(() => {
        setToast({
          type: TOAST_TYPE.ERROR,
          title: "Error!",
          message: "Custom properties could not be update. Please try again.",
        });
      });
  };

  if (issueTypeLoader === "init-loader") {
    return (
      <Loader className="space-y-4 py-4">
        <Loader.Item height="30px" />
        <Loader.Item height="30px" />
        <Loader.Item height="30px" />
        <Loader.Item height="30px" />
      </Loader>
    );
  }

  if (!issueTypeDetails || !activeProperties?.length) return null;

  return (
    <IssueAdditionalPropertyValues
      issueTypeId={issueTypeId}
      projectId={projectId}
      issuePropertyValues={issuePropertyValues ?? {}}
      variant="update"
      isPropertyValuesLoading={isLoading}
      handlePropertyValueChange={handlePropertyValueChange}
    />
  );
});
