"use client";

import { FC } from "react";
import { Avatar, Table } from "@plane/ui";
// helpers
import { convertMinutesToHoursMinutesString, renderFormattedDate } from "@/helpers/date-time.helper";
// hooks
import { useMember, useProject } from "@/hooks/store";
// plane web hooks
import { useWorkspaceWorklogs } from "@/plane-web/hooks/store";
// plane web types
import { TWorklog } from "@/plane-web/types";

export type TWorklogsPaginatedTableRoot = {
  workspaceSlug: string;
  workspaceId: string;
};

export const WorklogsPaginatedTableRoot: FC<TWorklogsPaginatedTableRoot> = (props) => {
  const {} = props;
  // hooks
  const { getProjectById } = useProject();
  const {
    workspace: { getWorkspaceMemberDetails },
  } = useMember();
  const { currentPaginatedKey, paginatedWorklogIds, worklogById } = useWorkspaceWorklogs();

  // derived values
  const worklogIds = currentPaginatedKey ? paginatedWorklogIds[currentPaginatedKey] : [];
  const worklogTableData = worklogIds.map((worklogId) => worklogById(worklogId)) as TWorklog[];

  const tableColumns = [
    {
      key: "project",
      content: "Project",
      tdRender: (rowData: TWorklog) => {
        const currentProject = (rowData.project_id && getProjectById(rowData.project_id)) || undefined;
        return <div className="truncate w-[200px]">{currentProject?.name}</div>;
      },
    },
    {
      key: "issue",
      content: "Issue",
      tdRender: (rowData: TWorklog) => {
        const currentProject = (rowData.project_id && getProjectById(rowData.project_id)) || undefined;
        return (
          <div className="flex items-center gap-2">
            <div className="text-xs text-custom-text-200">
              {currentProject?.identifier}-{rowData.issue_detail?.sequence_id}
            </div>
            <div className="text-custom-text-100">{rowData.issue_detail?.name || "undefined"}</div>
          </div>
        );
      },
    },
    {
      key: "logged",
      content: "Logged",
      tdRender: (rowData: TWorklog) => {
        const currentUser = (rowData.logged_by && getWorkspaceMemberDetails(rowData.logged_by)) || undefined;
        return (
          <div className="flex items-center gap-2">
            <Avatar
              name={currentUser?.member?.display_name}
              src={currentUser?.member?.avatar ?? undefined}
              shape="circle"
              size="sm"
              showTooltip={false}
            />
            <span className="flex-grow truncate">
              {currentUser?.member?.display_name} on {renderFormattedDate(rowData?.created_at)}
            </span>
          </div>
        );
      },
    },
    {
      key: "tile",
      content: "Time",
      tdRender: (rowData: TWorklog) => (
        <div className="font-medium">{rowData.duration && convertMinutesToHoursMinutesString(rowData.duration)}</div>
      ),
    },
  ];

  return (
    <div className="overflow-x-auto">
      <Table
        columns={tableColumns}
        data={worklogTableData}
        keyExtractor={(rowData: TWorklog) => rowData.id || ""}
        tableClassName="table-auto border-b border-custom-border-100"
        tHeadClassName="border-b border-custom-border-100"
        tHeadTrClassName="divide-x-0"
        thClassName="text-left p-2.5"
        tBodyClassName="divide-y-0"
        tBodyTrClassName="divide-x-0"
        tdClassName="p-2.5"
      />
    </div>
  );
};