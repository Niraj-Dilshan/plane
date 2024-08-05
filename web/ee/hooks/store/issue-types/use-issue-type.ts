import { useContext } from "react";
// context
import { StoreContext } from "@/lib/store-context";
// plane web stores
import { IIssueType } from "@/plane-web/store/issue-types";

export const useIssueType = (typeId: string | null | undefined): IIssueType | undefined => {
  const context = useContext(StoreContext);
  if (context === undefined) throw new Error("useIssueType must be used within StoreProvider");
  if (!typeId) {
    console.warn("useIssueType: typeId is not provided");
    return undefined;
  }
  const issueType = context.issueTypes.data?.[typeId];
  if (!issueType) {
    console.warn("useIssueType: issueType is not found");
  }
  return issueType;
};
